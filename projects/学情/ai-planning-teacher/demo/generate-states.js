const fs = require('fs');
const path = require('path');

const sourceFile = '/Users/a1-6/CC_project/projects/学情/ai-planning-teacher/demo/index-claude_副本.html';
const outputDir = '/Users/a1-6/CC_project/projects/学情/ai-planning-teacher/demo/figma-states';

// 创建输出目录
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// 读取源文件
const html = fs.readFileSync(sourceFile, 'utf-8');

// 定义所有状态
const states = [
  { name: '01-notify', page: 'notify', modal: null },
  { name: '02-invite', page: 'invite', modal: null },
  { name: '03-constraints', page: 'constraints', modal: null },
  { name: '04-waiting', page: 'waiting', modal: null },
  { name: '05-waiting-coscreen', page: 'waiting-coscreen', modal: null },
  { name: '06-review', page: 'review', modal: null },
  { name: '07-result', page: 'result', modal: null },
  { name: '08-result-self', page: 'result-self', modal: null },
  { name: '09-modal-code', page: 'invite', modal: 'mask-code' },
  { name: '10-modal-reject', page: 'review', modal: 'mask-reject' },
  { name: '11-modal-success', page: 'review', modal: 'mask-success' },
];

states.forEach(state => {
  let modifiedHtml = html;

  // 移除所有 active 类
  modifiedHtml = modifiedHtml.replace(/class="page active"/g, 'class="page"');
  modifiedHtml = modifiedHtml.replace(/class="mask active"/g, 'class="mask"');

  // 激活目标页面
  modifiedHtml = modifiedHtml.replace(
    new RegExp(`<div class="page" data-page="${state.page}">`),
    `<div class="page active" data-page="${state.page}">`
  );

  // 如果有弹窗，激活它
  if (state.modal) {
    modifiedHtml = modifiedHtml.replace(
      new RegExp(`<div class="mask" id="${state.modal}">`),
      `<div class="mask active" id="${state.modal}">`
    );
  }

  // 触发日历渲染（如果是 result 页面）
  if (state.page === 'result') {
    modifiedHtml = modifiedHtml.replace(
      '</body>',
      '<script>setTimeout(() => { renderCalendar(); }, 100);</script></body>'
    );
  }

  // 写入文件
  const outputPath = path.join(outputDir, `${state.name}.html`);
  fs.writeFileSync(outputPath, modifiedHtml);
  console.log(`Generated: ${state.name}.html`);
});

console.log(`\nAll ${states.length} states generated in: ${outputDir}`);
