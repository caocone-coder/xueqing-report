#!/usr/bin/env python3
import re
import os

source_file = '/Users/a1-6/CC_project/projects/学情/ai-planning-teacher/demo/index-claude_副本.html'
output_dir = '/Users/a1-6/CC_project/projects/学情/ai-planning-teacher/demo/figma-states'

# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

# 读取源文件
with open(source_file, 'r', encoding='utf-8') as f:
    html = f.read()

# 定义所有状态
states = [
    {'name': '01-notify', 'page': 'notify', 'modal': None},
    {'name': '02-invite', 'page': 'invite', 'modal': None},
    {'name': '03-constraints', 'page': 'constraints', 'modal': None},
    {'name': '04-waiting', 'page': 'waiting', 'modal': None},
    {'name': '05-waiting-coscreen', 'page': 'waiting-coscreen', 'modal': None},
    {'name': '06-review', 'page': 'review', 'modal': None},
    {'name': '07-result', 'page': 'result', 'modal': None},
    {'name': '08-result-self', 'page': 'result-self', 'modal': None},
    {'name': '09-modal-code', 'page': 'invite', 'modal': 'mask-code'},
    {'name': '10-modal-reject', 'page': 'review', 'modal': 'mask-reject'},
    {'name': '11-modal-success', 'page': 'review', 'modal': 'mask-success'},
]

for state in states:
    modified_html = html

    # 移除所有 active 类
    modified_html = re.sub(r'class="page active"', 'class="page"', modified_html)
    modified_html = re.sub(r'class="mask active"', 'class="mask"', modified_html)

    # 激活目标页面
    pattern = f'<div class="page" data-page="{state["page"]}">'
    replacement = f'<div class="page active" data-page="{state["page"]}">'
    modified_html = modified_html.replace(pattern, replacement)

    # 如果有弹窗，激活它
    if state['modal']:
        pattern = f'<div class="mask" id="{state["modal"]}">'
        replacement = f'<div class="mask active" id="{state["modal"]}">'
        modified_html = modified_html.replace(pattern, replacement)

    # 触发日历渲染（如果是 result 页面）
    if state['page'] == 'result':
        modified_html = modified_html.replace(
            '</body>',
            '<script>setTimeout(() => { if(typeof renderCalendar === "function") renderCalendar(); }, 100);</script></body>'
        )

    # 写入文件
    output_path = os.path.join(output_dir, f'{state["name"]}.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(modified_html)
    print(f'Generated: {state["name"]}.html')

print(f'\nAll {len(states)} states generated in: {output_dir}')
