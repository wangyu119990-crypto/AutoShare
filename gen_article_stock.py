from PIL import Image, ImageDraw, ImageFont
import os
from data_stock import stock_data

# ================= 配置区 =================
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1440
BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#333333"

# ✅ 字体修复：使用 Mac 系统字体
FONT_PATH = "/System/Library/Fonts/PingFang.ttc"

# ✅ 尺寸大调整 (根据 1080p 画布适配)
FONT_SIZE_TEXT = 42      # 正文文字大小
FONT_SIZE_EMOJI = 60     # 表头图标大小
LINE_SPACING = 60        # 行与行之间的空隙
SECTION_SPACING = 100    # 涨跌两大板块之间的距离

# 边距
MARGIN_LEFT = 80
MARGIN_TOP = 120
MARGIN_BOTTOM = 120

# 颜色
COLOR_UP = "#FF4D44"   # 涨：红
COLOR_DOWN = "#7DC067" # 跌：绿

def load_font(size):
    try:
        # 尝试加载 Mac 系统字体
        return ImageFont.truetype(FONT_PATH, size)
    except:
        # 如果失败，回退默认
        return ImageFont.load_default()

def create_new_page():
    img = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    return img, draw

def generate_stock_article():
    print("📄 正在生成美股排版 (字体修复版)...")
    
    # 准备输出目录
    output_dir = "stock_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 初始化
    current_page_index = 1
    img, draw = create_new_page()
    cursor_y = MARGIN_TOP
    
    font_text = load_font(FONT_SIZE_TEXT)
    font_emoji = load_font(FONT_SIZE_EMOJI) # 用来画大标题

    # --- 翻页检查函数 ---
    def check_paging(needed_height):
        nonlocal img, draw, cursor_y, current_page_index
        if cursor_y + needed_height > CANVAS_HEIGHT - MARGIN_BOTTOM:
            save_path = os.path.join(output_dir, f"article_p{current_page_index}.png")
            img.save(save_path)
            print(f"   --> 保存第 {current_page_index} 页")
            
            current_page_index += 1
            img, draw = create_new_page()
            cursor_y = MARGIN_TOP
            return True
        return False

    # --- 绘制板块函数 ---
    def draw_section(emoji_char, rect_color, data_list):
        nonlocal cursor_y, draw
        
        if not data_list:
            return

        # 1. 绘制表头 (表情 + 色块)
        # 预留高度
        header_height = 80
        check_paging(header_height + 50)

        # 绘制大大的 Emoji 或 替代文字
        # 提示：如果 Mac 依然显示方框，这里可以改成文字，比如 "【上涨】"
        draw.text((MARGIN_LEFT, cursor_y), emoji_char, font=font_emoji, fill="#000000")
        
        # 绘制色块 (在表情正下方)
        # 调整色块位置和大小以匹配新字号
        rect_x = MARGIN_LEFT
        rect_y = cursor_y + 85 # 在表情下方
        rect_width = 60        # 宽度
        rect_height = 25       # 高度
        
        draw.rectangle(
            [(rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height)], 
            fill=rect_color, outline=None
        )
        
        cursor_y += (header_height + 60) # 往下移动

        # 2. 绘制每一行数据
        for item in data_list:
            text_content = item['text']
            
            # 计算文字宽高
            bbox = draw.textbbox((0, 0), text_content, font=font_text)
            text_height = bbox[3] - bbox[1]
            
            check_paging(text_height + LINE_SPACING)
            
            # 绘制文字
            draw.text((MARGIN_LEFT, cursor_y), text_content, font=font_text, fill=TEXT_COLOR)
            
            cursor_y += (text_height + LINE_SPACING)
            
        cursor_y += SECTION_SPACING

    # --- 开始执行绘制 ---

    # 绘制上涨
    if "up_list" in stock_data:
        draw_section("📈", COLOR_UP, stock_data["up_list"])

    # 绘制下跌
    if "down_list" in stock_data:
        draw_section("📉", COLOR_DOWN, stock_data["down_list"])

    # 保存最后一页
    final_save_path = os.path.join(output_dir, f"article_p{current_page_index}.png")
    img.save(final_save_path)
    print(f"✅ 长图生成完毕: {final_save_path}")

if __name__ == "__main__":
    generate_stock_article()