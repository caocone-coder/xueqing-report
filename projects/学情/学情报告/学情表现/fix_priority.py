import openpyxl
import pandas as pd

file_path = '/Users/a1-6/CC_project/projects/学情/学情报告/学情表现/学情表现 v2.xlsx'
wb = openpyxl.load_workbook(file_path)
ws = wb.active

priority_map = {
    '薄弱知识点已攻克': '①-a',
    '知识点学扎实了': '①-b',
    '学习节节通关': '④-a',
    '单元内容已学透': '①-c',
    '知识点理解更深': '①-d',
    '课时练习接近满分': '②-a',
    '试卷练习发挥出色': '②-b',
    '题包正确率亮眼': '②-c',
    '预习任务全完成': '④-b',
    '本周计划全完成': '④-c',
    '答题连对记录': '②-d',
    '找到错题规律': '③-a',
    '错题一个个攻克': '③-b',
    '本周阅读时光': '⑤-a',
    '创意小画家': '⑥-a',
    '代码小工程师': '⑥-b',
    '实验小达人': '⑥-c',
    '作答过快，需关注': 'A⑥-f',
    '未使用答题技巧': 'A⑥-g',
    '学习中途退出偏多': 'A⑥-h',
    '答题可以更认真': 'A⑥-a',
    '试试用学习资源': 'A⑥-b',
    '再坚持一下就攻克了': 'A⑥-c',
    '学习时间少了一些': 'A④-a',
    '[学科]可以多花点时间': 'A④-b',
    '[学科]好久没碰了': 'A④-c',
    '这些知识点还不太熟': 'A①-a',
    '这个知识点要多练练': 'A①-b',
    '同类题反复出错': 'A①-c',
    '学过的知识点有点生了': 'A①-d',
    '正确率有提升空间': 'A③-a',
    '单词还要多记记': 'A③-b',
    '作业可以再抓紧些': 'A⑤-a',
    '学习计划落后了一点': 'A⑤-b',
    '单词该复习了': 'A⑤-c',
    '错题还没订正': 'A②-a',
    '审题可以再仔细些': 'A②-b',
    '错题还没分析原因': 'A②-c',
    '答题习惯需关注': 'A⑥-d',
    '批改结果被修改了': 'A⑥-e',
    '好久没画画了': 'A⑧-a',
    '好久没编程了': 'A⑧-b',
    '好久没做实验了': 'A⑧-c',
    '该运动一下了': 'A⑧-d',
    '专注时间可以更长': 'A⑦-a',
    '注意保护眼睛': 'A⑦-b',
}

# Col 3 has wrong data (priority values), Col 4 should have priority
# First, clear col 3 and move name back, then write priority to col 4
for row_idx in range(2, ws.max_row + 1):
    name_val = ws.cell(row_idx, 3).value
    if name_val and name_val in priority_map:
        # Col 3 has priority value, need to restore name
        # The name should be in the map key
        ws.cell(row_idx, 3).value = name_val  # Keep as is for now
        ws.cell(row_idx, 4).value = priority_map[name_val]
    else:
        # Col 3 might already have the correct name
        # Try to find priority from the name
        for name_key, pri_val in priority_map.items():
            if name_key in str(name_val):
                ws.cell(row_idx, 4).value = pri_val
                break

wb.save(file_path)
print(f'Fixed priority column in {file_path}')
