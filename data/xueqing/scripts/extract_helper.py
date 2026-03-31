#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据提取辅助脚本
用于批量处理图片识别任务
"""

import os
import json


def generate_extraction_prompt(image_path, row_num):
    """
    生成用于 Claude 识别的提示词

    Args:
        image_path: 图片路径
        row_num: 行号

    Returns:
        str: 提示词
    """
    prompt = f"""
请分析图片 {image_path} (源文件行号: {row_num})

这是一个学习机用户成长案例的营销海报。请从图片中提取以下 18 个字段的信息。
如果某个字段在图片中找不到，请填写"无"。

必须提取的字段:
1. 对象名称（内容名称） - 案例的标题或主题
2. 对象ID（内容id） - 通常是数字编号
3. 对象类型 - 固定为 "MODEL"
4. 适用学科 - 如: 数学、语文、英语等
5. 适用学段 - 如: 小学、初中、高中
6. 适用年级 - 如: 一年级、二年级等
7. 适用机型 - 设备型号列表
8. 适用场景 - 如: 预习类、复习类、备考类
9. 适用难度 - 如: 基础、进阶、拔高
10. 用户名称 - 学生的名字或昵称
11. 用户天数 - 使用设备的天数（整数）
12. 用户个人标签 - 用户特征标签
13. 用户所属城市 - 城市名称
14. 使用机型 - 具体使用的设备型号
15. 成效学科 - 取得成效的学科
16. 内容发布时间 - 发布日期
17. 包含应用 - 使用的应用列表
18. 内容详情 - 详情页 URL

请以 JSON 格式返回，格式如下:
{{
  "对象名称（内容名称）": "...",
  "对象ID（内容id）": "...",
  "对象类型": "MODEL",
  "适用学科": "...",
  "适用学段": "...",
  "适用年级": "...",
  "适用机型": "...",
  "适用场景": "...",
  "适用难度": "...",
  "用户名称": "...",
  "用户天数": "...",
  "用户个人标签": "...",
  "用户所属城市": "...",
  "使用机型": "...",
  "成效学科": "...",
  "内容发布时间": "...",
  "包含应用": "...",
  "内容详情": "..."
}}

请将提取的 JSON 数据保存到: /Users/a1-6/CC_project/data/xueqing/output/temp_row_{row_num}.json
"""
    return prompt


def main():
    base_dir = "/Users/a1-6/CC_project/data/xueqing"
    mapping_file = os.path.join(base_dir, "output/row_to_image_mapping.json")

    with open(mapping_file, 'r') as f:
        image_mapping = json.load(f)

    print("=== 数据提取任务列表 ===\n")

    for row_num_str, image_path in sorted(image_mapping.items(), key=lambda x: int(x[0]))[:5]:
        row_num = int(row_num_str)
        print(f"\n--- 行 {row_num} ---")
        print(generate_extraction_prompt(image_path, row_num))
        print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
