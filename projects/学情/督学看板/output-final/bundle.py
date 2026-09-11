#!/usr/bin/env python3
"""
Bundle multiple HTML pages into a single self-contained HTML file.
"""
import re
from pathlib import Path

# Source files mapping
SOURCES = {
    'page-customer-unauthorized': '/Users/a1-6/Desktop/客户详情页.html',
    'page-wechat-chat': '/Users/a1-6/Desktop/企微聊天页.html',
    'page-auth-request': '/Users/a1-6/Desktop/伴学授权申请.html',
    'page-customer-authorized': '/Users/a1-6/CC_project/projects/学情/督学看板/output/customer-detail.html',
    'page-dashboard': '/Users/a1-6/CC_project/projects/学情/督学看板/output/dashboard.html',
    'page-student-report': '/Users/a1-6/CC_project/projects/student-performance-report/index.html',
}

# Navigation mapping for replacement
NAV_MAPPING = {
    "window.location.href='/Users/a1-6/Desktop/伴学授权申请.html'": "navigateTo('page-auth-request')",
    "window.location.href='企微聊天页.html'": "navigateTo('page-wechat-chat')",
    "window.location.href='客户详情页.html'": "navigateTo('page-customer-unauthorized')",
    "window.location.href='伴学授权申请.html'": "navigateTo('page-auth-request')",
    "window.location.href = '/Users/a1-6/CC_project/projects/%E5%AD%A6%E6%83%85/%E7%9D%A3%E5%AD%A6%E7%9C%8B%E6%9D%BF/output/customer-detail.html'": "navigateTo('page-customer-authorized')",
    "window.location.href='/Users/a1-6/Desktop/伴学授权申请.html'": "navigateTo('page-auth-request')",
    "location.href='report-detail.html'": "navigateTo('page-dashboard')",
    "location.href='/Users/a1-6/CC_project/projects/student-performance-report/index.html'": "navigateTo('page-student-report')",
    "onclick=\"history.back()\"": "onclick=\"goBack()\"",
    "href=\"dashboard.html\"": "href=\"javascript:navigateTo('page-dashboard')\"",
    "href='customer-detail.html'": "href=\"javascript:navigateTo('page-customer-authorized')\"",
    "window.location.href='cuoti-detail.html'": "return false",  # Disable non-existent pages
}

def extract_styles(html_content):
    """Extract all <style> tags from HTML."""
    style_pattern = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL)
    styles = style_pattern.findall(html_content)
    return '\n'.join(styles)

def extract_body(html_content):
    """Extract content inside <body> tag."""
    body_pattern = re.compile(r'<body[^>]*>(.*?)</body>', re.DOTALL)
    match = body_pattern.search(html_content)
    return match.group(1) if match else ''

def extract_scripts(html_content):
    """Extract all <script> tags from HTML."""
    script_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL)
    scripts = script_pattern.findall(html_content)
    return '\n'.join(scripts)

def scope_styles(styles, page_id):
    """Add page ID scope to CSS selectors to avoid conflicts."""
    # Don't scope: @, :root, *, html, body, keyframes
    lines = styles.split('\n')
    scoped = []
    in_keyframes = False

    for line in lines:
        stripped = line.strip()

        # Track keyframes blocks
        if '@keyframes' in stripped or '@-webkit-keyframes' in stripped:
            in_keyframes = True
            scoped.append(line)
            continue
        if in_keyframes:
            scoped.append(line)
            if '}' in stripped:
                in_keyframes = False
            continue

        # Don't scope these
        if (stripped.startswith('@') or
            stripped.startswith('*') or
            stripped.startswith('html') or
            stripped.startswith('body') or
            ':root' in stripped or
            not stripped or
            stripped.startswith('}')):
            scoped.append(line)
            continue

        # Scope regular selectors
        if '{' in line and not line.strip().startswith('@'):
            # Extract selector part
            parts = line.split('{', 1)
            selector = parts[0].strip()
            rest = '{' + parts[1] if len(parts) > 1 else ''

            # Add scope
            if selector and not selector.startswith('#' + page_id):
                scoped_selector = f"#{page_id} {selector}"
                scoped.append(f"  {scoped_selector} {rest}")
            else:
                scoped.append(line)
        else:
            scoped.append(line)

    return '\n'.join(scoped)

def replace_navigation(content):
    """Replace navigation calls with SPA navigation."""
    for old, new in NAV_MAPPING.items():
        content = content.replace(old, new)
    return content

def main():
    print("Starting bundle process...")

    all_styles = []
    all_bodies = []
    all_scripts = []

    # Process each source file
    for page_id, file_path in SOURCES.items():
        print(f"Processing {page_id} from {file_path}...")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract components
        styles = extract_styles(content)
        body = extract_body(content)
        scripts = extract_scripts(content)

        # Scope styles
        scoped_styles = scope_styles(styles, page_id)
        all_styles.append(f"\n/* ===== {page_id} styles ===== */\n{scoped_styles}")

        # Replace navigation in body
        body = replace_navigation(body)

        # Wrap body in page div
        active_class = ' active' if page_id == 'page-customer-unauthorized' else ''
        wrapped_body = f'\n  <!-- ===== {page_id} ===== -->\n  <div id="{page_id}" class="page{active_class}">\n{body}\n  </div>\n'
        all_bodies.append(wrapped_body)

        # Replace navigation in scripts
        scripts = replace_navigation(scripts)
        all_scripts.append(f"\n/* ===== {page_id} scripts ===== */\n{scripts}")

    # Build final HTML
    final_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>督学看板 - 完整流程</title>
  <style>
    /* Global page switching */
    .page {{
      display: none;
    }}
    .page.active {{
      display: block;
    }}

    /* Global resets - apply to all pages */
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

{''.join(all_styles)}
  </style>
</head>
<body>
{''.join(all_bodies)}

  <script>
    /* ===== Global Navigation System ===== */
    const pageHistory = ['page-customer-unauthorized'];

    function showPage(pageId) {{
      document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
      const targetPage = document.getElementById(pageId);
      if (targetPage) {{
        targetPage.classList.add('active');
        window.scrollTo(0, 0);
      }} else {{
        console.error('Page not found:', pageId);
      }}
    }}

    function navigateTo(pageId) {{
      pageHistory.push(pageId);
      showPage(pageId);
    }}

    function goBack() {{
      if (pageHistory.length > 1) {{
        pageHistory.pop();
        showPage(pageHistory[pageHistory.length - 1]);
      }}
    }}

{''.join(all_scripts)}
  </script>
</body>
</html>"""

    # Write output
    output_path = Path(__file__).parent / 'index.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"✓ Bundle created: {output_path}")
    print(f"  Total size: {len(final_html) / 1024 / 1024:.2f} MB")

if __name__ == '__main__':
    main()
