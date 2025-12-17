import os
from jinja2 import Template
from playwright.sync_api import sync_playwright

def create_cover(date_text, main_text):
    print(f"正在生成封面：日期={date_text}, 文字={main_text}...")
    
    # 1. 获取当前路径
    current_dir = os.getcwd()
    
    # 2. 读取 HTML 模具
    with open('cover_template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 3. 填入文字
    template = Template(template_content)
    html_rendered = template.render(date_text=date_text, main_text=main_text)
    
    # ---【关键修改】---
    # 我们不再直接塞内容，而是先把填好的 HTML 保存为一个临时文件
    # 这样浏览器打开它时，绝对能找到旁边的图片
    temp_html_path = os.path.join(current_dir, "temp_cover.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_rendered)
    
    # 4. 启动浏览器拍照
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1245, 'height': 1660})
        
        # 让浏览器打开这个本地文件 (file://...)
        # 这比 set_content 稳定 100 倍
        page.goto(f"file://{temp_html_path}")
        
        output_filename = "final_cover.png"
        page.screenshot(path=output_filename)
        
        browser.close()
        
    # (可选) 删掉临时文件，保持干净
    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)

    print(f"✅ 成功！封面已保存为：{output_filename}")

if __name__ == "__main__":
    test_date = "2025.11.21"
    test_quote = "终极修复版！\n这次绝对没有红色报错了。"
    
    create_cover(test_date, test_quote)