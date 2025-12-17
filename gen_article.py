import os
import markdown
import textwrap
from jinja2 import Template
from playwright.sync_api import sync_playwright

# ==================== 尺寸配置：1245 × 1660 ====================
PAGE_WIDTH = 1245
PAGE_HEIGHT = 1660

# 边距设置
MARGIN_TOP_FIRST = 225   # 第一页上边距
MARGIN_TOP_OTHERS = 105  # 其他页上边距
MARGIN_BOTTOM = 50       # 底部边距（安全区域）

# 分页高度限制（实际可用高度）
MAX_PAGE_HEIGHT_FIRST = PAGE_HEIGHT - MARGIN_TOP_FIRST - MARGIN_BOTTOM   # 1385
MAX_PAGE_HEIGHT_OTHERS = PAGE_HEIGHT - MARGIN_TOP_OTHERS - MARGIN_BOTTOM # 1505
# ================================================================

def get_html_height(page, html_content, template_content, is_first_page):
    """计算 HTML 内容的高度"""
    template = Template(template_content)
    full_html = template.render(content_html=html_content, is_first_page=is_first_page)
    page.set_content(full_html, wait_until="domcontentloaded")
    height = page.evaluate("document.querySelector('.container').scrollHeight")
    # 加上顶部边距
    margin_top = MARGIN_TOP_FIRST if is_first_page else MARGIN_TOP_OTHERS
    return height + margin_top

def render_final_image(page, template_content, html_content, filename, is_first_page):
    """渲染最终图片"""
    template = Template(template_content)
    final_html = template.render(content_html=html_content, is_first_page=is_first_page)
    current_dir = os.getcwd()
    temp_path = os.path.join(current_dir, "temp_render.html")
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    page.goto(f"file://{temp_path}")
    # 设置视口为 1245 × 1660
    page.set_viewport_size({'width': PAGE_WIDTH, 'height': PAGE_HEIGHT})
    page.screenshot(path=filename)
    if os.path.exists(temp_path):
        os.remove(temp_path)
    print(f"✅ 已生成：{filename} (尺寸: {PAGE_WIDTH}×{PAGE_HEIGHT})")

def create_smart_slides(title, raw_content):
    """创建智能分页的幻灯片"""
    print(f"正在进行智能排版计算（尺寸：{PAGE_WIDTH}×{PAGE_HEIGHT}）...")
    with open('article_template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # 使用足够高的 viewport 用于计算高度
        page = browser.new_page(viewport={'width': PAGE_WIDTH, 'height': 3000})
        
        full_text = textwrap.dedent(raw_content).strip()
        raw_sections = [s for s in full_text.split('## ') if s.strip()]
        
        product_html_list = []
        for section in raw_sections:
            # --- 强制修复简介位置 ---
            section = section.replace("\n简介：", "\n\n简介：")
            
            md_text = "## " + section
            html_part = markdown.markdown(md_text)
            product_html_list.append(f'<div class="product-block">{html_part}</div>')

        current_page_products = []
        page_count = 1
        
        for product_html in product_html_list:
            is_first_page = (page_count == 1)
            trial_list = current_page_products + [product_html]
            trial_html_str = "<hr>".join(trial_list)
            height = get_html_height(page, trial_html_str, template_content, is_first_page)
            
            # 根据页面类型选择不同的高度限制
            max_height = MAX_PAGE_HEIGHT_FIRST if is_first_page else MAX_PAGE_HEIGHT_OTHERS
            
            if height < max_height:
                current_page_products.append(product_html)
            else:
                if current_page_products:
                    final_str = "<hr>".join(current_page_products)
                    render_final_image(page, template_content, final_str, f"slide_{page_count}.png", page_count == 1)
                    page_count += 1
                current_page_products = [product_html]
        
        if current_page_products:
            final_str = "<hr>".join(current_page_products)
            render_final_image(page, template_content, final_str, f"slide_{page_count}.png", page_count == 1)

        browser.close()
        print(f"\n✅ 共生成 {page_count} 页，每页尺寸：{PAGE_WIDTH}×{PAGE_HEIGHT}")

if __name__ == "__main__":
    pass