import os
import importlib
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import data_stock

# ================= 配置区 =================
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "stock_output"

# 页面基础参数 - 修改为 1245×1660
# 缩放比例：1245/1080 = 1660/1440 = 1.15278
PAGE_HEIGHT = 1660  # 1440 * 1.153 = 1660
PADDING_TOP = 115   # 100 * 1.153 = 115
PADDING_BOTTOM = 115  # 100 * 1.153 = 115
AVAILABLE_HEIGHT = PAGE_HEIGHT - PADDING_TOP - PADDING_BOTTOM  # 1430

# === 布局方案配置 ===
# 1. 标准宽松模式 (默认) - 所有尺寸按 1.153 比例缩放
LAYOUT_STANDARD = {
    "gap": 46,      # 40 * 1.153 = 46
    "spacer": 115,  # 100 * 1.153 = 115
    "h_row": 105,   # 91 * 1.153 = 105
    "h_header": 208  # 180 * 1.153 = 208
}

# 2. 紧凑压缩模式 (当出现孤儿行时启用) - 所有尺寸按 1.153 比例缩放
LAYOUT_TIGHT = {
    "gap": 29,      # 25 * 1.153 = 29
    "spacer": 92,   # 80 * 1.153 = 92
    "h_row": 88,    # 76 * 1.153 = 88
    "h_header": 208  # 180 * 1.153 = 208
}

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def render_html(template_name, data):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_name)
    return template.render(**data)

# === 核心：通用分页计算器 ===
def calculate_pages(stock_data, layout):
    pages = []
    current_page_content = []
    current_height_used = 0
    
    # 提取布局参数
    H_ROW = layout["h_row"]
    H_HEADER = layout["h_header"]
    H_SPACER = layout["spacer"]

    def start_new_page():
        nonlocal current_page_content, current_height_used
        if current_page_content:
            pages.append({"content": current_page_content})
        current_page_content = []
        current_height_used = 0

    def add_block(block_type, data, height_cost):
        nonlocal current_height_used
        if current_height_used + height_cost > AVAILABLE_HEIGHT:
            if block_type == 'spacer': return 
            start_new_page()
        
        current_page_content.append({"type": block_type, **data})
        current_height_used += height_cost

    # --- 1. 上涨 ---
    # 🚨 核心修改：使用 stock_content_formatted (详细数据) 而不是 up_list (简略列表)
    stock_content = stock_data.get("stock_content_formatted", "")
    if stock_content:
        # 将 stock_content_formatted 字符串按行分割，过滤空行，分离上涨和下跌
        content_lines = [line.strip() for line in stock_content.split('\n') if line.strip()]
        
        up_lines = [line for line in content_lines if line.startswith('📈')]
        down_lines = [line for line in content_lines if line.startswith('📉')]
        
        # 显示上涨股票
        if up_lines:
            add_block('header', {"emoji": "📈", "color_class": "bg-red"}, H_HEADER)
            
            current_rows_buffer = []
            for item in up_lines:
                if current_height_used + H_ROW > AVAILABLE_HEIGHT:
                    if current_rows_buffer:
                        current_page_content.append({"type": "list", "rows": current_rows_buffer})
                        current_rows_buffer = []
                    start_new_page()
                    add_block('header', {"emoji": "📈", "color_class": "bg-red"}, H_HEADER)
                
                current_rows_buffer.append({"text": item})
                current_height_used += H_ROW
                
            if current_rows_buffer:
                current_page_content.append({"type": "list", "rows": current_rows_buffer})

    # --- 2. 下跌 ---
    # 优先使用 stock_content_formatted 中的下跌数据，如果没有则使用 down_list
    stock_content = stock_data.get("stock_content_formatted", "")
    down_lines_from_content = []
    if stock_content:
        content_lines = [line.strip() for line in stock_content.split('\n') if line.strip()]
        down_lines_from_content = [line for line in content_lines if line.startswith('📉')]
    
    down_list = stock_data.get("down_list", [])
    if down_lines_from_content or down_list:
        if current_height_used > 0:
            add_block('spacer', {}, H_SPACER)

        add_block('header', {"emoji": "📉", "color_class": "bg-green"}, H_HEADER)
        
        # 使用 stock_content_formatted 中的下跌数据，如果没有则使用 down_list
        down_items = down_lines_from_content if down_lines_from_content else down_list
        
        current_rows_buffer = []
        for item in down_items:
            if current_height_used + H_ROW > AVAILABLE_HEIGHT:
                if current_rows_buffer:
                    current_page_content.append({"type": "list", "rows": current_rows_buffer})
                    current_rows_buffer = []
                start_new_page()
                add_block('header', {"emoji": "📉", "color_class": "bg-green"}, H_HEADER)
            
            current_rows_buffer.append({"text": item})
            current_height_used += H_ROW
            
        if current_rows_buffer:
            current_page_content.append({"type": "list", "rows": current_rows_buffer})

    start_new_page()
    return pages

# === 智能布局优化器 ===
def get_smart_pages(stock_data):
    print("🤖 正在计算最佳布局...")
    
    # 1. 先试用【标准布局】计算
    pages_std = calculate_pages(stock_data, LAYOUT_STANDARD)
    
    if len(pages_std) <= 1:
        print("   -> 内容较少，使用标准布局 (1页)")
        return pages_std, LAYOUT_STANDARD
    
    last_page = pages_std[-1]
    item_count = 0
    for block in last_page["content"]:
        if block["type"] == "list":
            item_count += len(block["rows"])
    
    if item_count <= 1:
        print(f"   ⚠️ 发现孤儿页 (最后一页只有 {item_count} 条数据)！尝试压缩...")
        pages_tight = calculate_pages(stock_data, LAYOUT_TIGHT)
        if len(pages_tight) < len(pages_std):
            print("   ✅ 压缩成功！使用紧凑布局。")
            return pages_tight, LAYOUT_TIGHT
        else:
            print("   ❌ 压缩失败。保持标准布局。")
            return pages_std, LAYOUT_STANDARD
    
    print("   -> 布局正常，使用标准布局")
    return pages_std, LAYOUT_STANDARD

def get_yesterday_cn_date():
    """
    计算"今天 - 1 天"的日期，并格式化为 `M月D日`，例如 12月4日。
    说明：与 gen_cover_stock 保持一致，美股封面的展示日期统一按照
    "系统当前日期 - 1 天" 来生成，而不是直接使用 data_stock.date_str。
    """
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%m月%d日")


def run_task():
    import data_stock
    importlib.reload(data_stock)

    print("🚀 启动 Playwright (智能孤儿控制版)...")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 1. 封面
        cover_data = {"date_str": get_yesterday_cn_date()}
        html_cover = render_html("stock_cover.html", cover_data)
        
        cover_html_path = os.path.join(OUTPUT_DIR, "debug_cover.html")
        with open(cover_html_path, "w", encoding="utf-8") as f:
            f.write(html_cover)
            
        page.set_viewport_size({"width": 1245, "height": 1660})
        page.goto(f"file://{os.path.abspath(cover_html_path)}")
        page.wait_for_timeout(500) 
        page.screenshot(path=os.path.join(OUTPUT_DIR, "cover_final.png"))

        # 2. 内容页
        final_pages, final_layout = get_smart_pages(data_stock.stock_data)
        
        html_article = render_html("stock_article.html", {
            "pages": final_pages,
            "layout": final_layout
        })
        
        article_html_path = os.path.join(OUTPUT_DIR, "debug_article.html")
        with open(article_html_path, "w", encoding="utf-8") as f:
            f.write(html_article)
            
        page.set_viewport_size({"width": 1245, "height": 1660})
        page.goto(f"file://{os.path.abspath(article_html_path)}")
        page.wait_for_timeout(500)
        
        page_elements = page.query_selector_all(".page")
        for index, element in enumerate(page_elements):
            save_path = os.path.join(OUTPUT_DIR, f"article_p{index + 1}.png")
            element.screenshot(path=save_path)
            print(f"   ✅ 已保存: {save_path}")

        browser.close()

if __name__ == "__main__":
    run_task()
