#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证模块
验证提取数据的完整性和格式
"""

import json


class DataValidator:
    # 18 个必需字段
    REQUIRED_FIELDS = [
        "对象名称（内容名称）",
        "对象ID（内容id）",
        "对象类型",
        "适用学科",
        "适用学段",
        "适用年级",
        "适用机型",
        "适用场景",
        "适用难度",
        "用户名称",
        "用户天数",
        "用户个人标签",
        "用户所属城市",
        "使用机型",
        "成效学科",
        "内容发布时间",
        "包含应用",
        "内容详情"
    ]

    def __init__(self):
        self.validation_results = []

    def validate_field_count(self, data_dict):
        """
        验证字段数量

        Args:
            data_dict: 数据字典

        Returns:
            tuple: (is_valid, missing_fields)
        """
        missing_fields = []
        for field in self.REQUIRED_FIELDS:
            if field not in data_dict:
                missing_fields.append(field)

        is_valid = len(missing_fields) == 0
        return is_valid, missing_fields

    def validate_field_format(self, data_dict):
        """
        验证字段格式

        Args:
            data_dict: 数据字典

        Returns:
            list: 格式错误列表
        """
        errors = []

        # 验证对象ID（应该是数字或特定格式）
        obj_id = data_dict.get("对象ID（内容id）", "")
        if obj_id and obj_id != "无":
            if not any(char.isdigit() for char in str(obj_id)):
                errors.append(f"对象ID格式错误: {obj_id}")

        # 验证用户天数（应该是整数）
        user_days = data_dict.get("用户天数", "")
        if user_days and user_days != "无":
            try:
                days = int(str(user_days).replace("天", "").strip())
                if days < 0 or days > 3650:
                    errors.append(f"用户天数超出合理范围: {days}")
            except ValueError:
                errors.append(f"用户天数格式错误: {user_days}")

        return errors

    def validate_row(self, row_num, data_dict):
        """
        验证单行数据

        Args:
            row_num: 行号
            data_dict: 数据字典

        Returns:
            dict: 验证结果
        """
        is_valid_count, missing_fields = self.validate_field_count(data_dict)
        format_errors = self.validate_field_format(data_dict)

        result = {
            'row_num': row_num,
            'is_valid': is_valid_count and len(format_errors) == 0,
            'missing_fields': missing_fields,
            'format_errors': format_errors
        }

        self.validation_results.append(result)
        return result

    def generate_report(self, output_file):
        """
        生成验证报告

        Args:
            output_file: 输出文件路径
        """
        total = len(self.validation_results)
        valid_count = sum(1 for r in self.validation_results if r['is_valid'])
        invalid_count = total - valid_count

        report = {
            'summary': {
                'total': total,
                'valid': valid_count,
                'invalid': invalid_count,
                'success_rate': f"{valid_count/total*100:.2f}%" if total > 0 else "0%"
            },
            'details': self.validation_results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n=== 验证报告 ===")
        print(f"总计: {total} 行")
        print(f"有效: {valid_count} 行")
        print(f"无效: {invalid_count} 行")
        print(f"成功率: {report['summary']['success_rate']}")
        print(f"详细报告已保存: {output_file}")
