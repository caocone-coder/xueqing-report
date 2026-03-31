#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主控制脚本 - 半自动化版本
协调图片下载、数据提取、Excel 写入
"""

import os
import sys
import json
import argparse
from datetime import datetime

# 导入自定义模块
from image_downloader import ImageDownloader
from excel_handler import ExcelHandler
from data_validator import DataValidator


class MainController:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.source_file = os.path.join(base_dir, "model 数据.xlsx")
        self.target_file = os.path.join(base_dir, "model 配置表.xlsx")
        self.temp_images_dir = os.path.join(base_dir, "temp_images")
        self.logs_dir = os.path.join(base_dir, "logs")
        self.output_dir = os.path.join(base_dir, "output")

        # 初始化模块
        self.downloader = ImageDownloader(self.temp_images_dir)
        self.excel_handler = ExcelHandler(self.source_file, self.target_file)
        self.validator = DataValidator()

        # 数据存储
        self.extracted_data_file = os.path.join(self.output_dir, "extracted_data.json")
        self.extracted_data = {}

    def mode_download(self):
        """模式1: 下载图片"""
        print("\n=== 模式: 下载图片 ===\n")

        # 读取源文件 URL
        url_dict = self.excel_handler.read_source_urls(column='K')

        if not url_dict:
            print("错误: 未找到任何 URL")
            return False

        # 批量下载
        results = self.downloader.batch_download(url_dict)

        # 保存下载日志
        log_file = os.path.join(self.logs_dir, f"download_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.downloader.save_log(log_file)

        # 保存下载结果映射
        mapping_file = os.path.join(self.output_dir, "row_to_image_mapping.json")
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"图片路径映射已保存: {mapping_file}")

        return True

    def mode_extract_interactive(self):
        """模式2: 交互式数据提取（需要人工配合）"""
        print("\n=== 模式: 交互式数据提取 ===\n")
        print("此模式需要您配合 Claude Code 逐张识别图片")
        print("请按照以下步骤操作:\n")

        # 加载图片路径映射
        mapping_file = os.path.join(self.output_dir, "row_to_image_mapping.json")
        if not os.path.exists(mapping_file):
            print(f"错误: 未找到映射文件 {mapping_file}")
            print("请先运行: python3 main.py --mode download")
            return False

        with open(mapping_file, 'r', encoding='utf-8') as f:
            image_mapping = json.load(f)

        # 加载已提取的数据（如果存在）
        if os.path.exists(self.extracted_data_file):
            with open(self.extracted_data_file, 'r', encoding='utf-8') as f:
                self.extracted_data = json.load(f)
            print(f"已加载 {len(self.extracted_data)} 条已提取的数据\n")

        # 获取目标字段
        headers = self.excel_handler.read_target_headers()

        print(f"总计需要处理 {len(image_mapping)} 张图片")
        print("=" * 60)

        for row_num_str, image_path in sorted(image_mapping.items(), key=lambda x: int(x[0])):
            row_num = int(row_num_str)

            # 跳过已处理的行
            if str(row_num) in self.extracted_data:
                print(f"[跳过] 行 {row_num} 已处理")
                continue

            print(f"\n处理行 {row_num}:")
            print(f"图片路径: {image_path}")
            print("\n请使用 Claude Code 的 Read 工具查看此图片，并提取以下 18 个字段:")
            for i, field in enumerate(headers, 1):
                print(f"  {i}. {field}")

            print("\n提取完成后，请将数据以 JSON 格式粘贴到文件:")
            temp_json_file = os.path.join(self.output_dir, f"temp_row_{row_num}.json")
            print(f"  {temp_json_file}")

            input(f"\n按 Enter 继续处理下一张图片...")

            # 尝试读取临时 JSON 文件
            if os.path.exists(temp_json_file):
                try:
                    with open(temp_json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # 验证数据
                    validation_result = self.validator.validate_row(row_num, data)
                    if validation_result['is_valid']:
                        self.extracted_data[str(row_num)] = data
                        print(f"✓ 行 {row_num} 数据已保存")

                        # 保存到主文件
                        with open(self.extracted_data_file, 'w', encoding='utf-8') as f:
                            json.dump(self.extracted_data, f, ensure_ascii=False, indent=2)

                        # 删除临时文件
                        os.remove(temp_json_file)
                    else:
                        print(f"✗ 行 {row_num} 数据验证失败:")
                        if validation_result['missing_fields']:
                            print(f"  缺失字段: {validation_result['missing_fields']}")
                        if validation_result['format_errors']:
                            print(f"  格式错误: {validation_result['format_errors']}")
                except Exception as e:
                    print(f"✗ 读取临时文件失败: {e}")
            else:
                print(f"⚠ 未找到临时文件，跳过此行")

        print(f"\n提取完成! 共提取 {len(self.extracted_data)} 行数据")
        return True

    def mode_write(self):
        """模式3: 写入数据到目标 Excel"""
        print("\n=== 模式: 写入数据 ===\n")

        # 加载提取的数据
        if not os.path.exists(self.extracted_data_file):
            print(f"错误: 未找到数据文件 {self.extracted_data_file}")
            print("请先运行: python3 main.py --mode extract_interactive")
            return False

        with open(self.extracted_data_file, 'r', encoding='utf-8') as f:
            self.extracted_data = json.load(f)

        if not self.extracted_data:
            print("错误: 没有可写入的数据")
            return False

        print(f"加载了 {len(self.extracted_data)} 行数据")

        # 获取目标字段顺序
        headers = self.excel_handler.read_target_headers()

        # 转换为列表格式
        data_list = []
        for row_num_str in sorted(self.extracted_data.keys(), key=lambda x: int(x)):
            data_dict = self.extracted_data[row_num_str]
            row_data = [data_dict.get(field, "无") for field in headers]
            data_list.append(row_data)

        # 创建备份
        self.excel_handler.create_backup(self.output_dir)

        # 写入数据
        success = self.excel_handler.append_data_to_target(data_list)

        if success:
            print("\n✓ 数据写入成功!")

            # 生成验证报告
            report_file = os.path.join(self.logs_dir, f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            self.validator.generate_report(report_file)
        else:
            print("\n✗ 数据写入失败")

        return success

    def mode_validate(self):
        """模式4: 验证数据"""
        print("\n=== 模式: 验证数据 ===\n")

        # 加载提取的数据
        if not os.path.exists(self.extracted_data_file):
            print(f"错误: 未找到数据文件 {self.extracted_data_file}")
            return False

        with open(self.extracted_data_file, 'r', encoding='utf-8') as f:
            self.extracted_data = json.load(f)

        # 验证每一行
        for row_num_str, data_dict in self.extracted_data.items():
            self.validator.validate_row(int(row_num_str), data_dict)

        # 生成报告
        report_file = os.path.join(self.logs_dir, f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.validator.generate_report(report_file)

        return True


def main():
    parser = argparse.ArgumentParser(description='Excel 图片数据提取工具')
    parser.add_argument('--mode', required=True,
                       choices=['download', 'extract_interactive', 'write', 'validate'],
                       help='运行模式')
    parser.add_argument('--base-dir', default='/Users/a1-6/CC_project/data/xueqing',
                       help='基础目录路径')

    args = parser.parse_args()

    # 初始化控制器
    controller = MainController(args.base_dir)

    # 根据模式执行
    if args.mode == 'download':
        success = controller.mode_download()
    elif args.mode == 'extract_interactive':
        success = controller.mode_extract_interactive()
    elif args.mode == 'write':
        success = controller.mode_write()
    elif args.mode == 'validate':
        success = controller.mode_validate()
    else:
        print(f"未知模式: {args.mode}")
        success = False

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
