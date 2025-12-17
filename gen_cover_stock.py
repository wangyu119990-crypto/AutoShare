from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime, timedelta
from data_stock import stock_data

# ================= 配置区 =================
CANVAS_WIDTH = 1245
CANVAS_HEIGHT = 1660

# ✅ 核心修改：直接使用 Mac 系统自带的苹方字体，解决乱码
# 注意：如果你是 Windows，这里需要改成 "C:/Windows/Fonts/msyh.ttc" (微软雅黑)
FONT_PATH = "/System/Library/Fonts/PingFang.ttc"


def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        print(f"⚠️ 依然找不到字体: {FONT_PATH}，尝试使用默认")
        return ImageFont.load_default()


def get_yesterday_cn_date():
    """
    计算"今天 - 1 天"的日期，并格式化为 `M月D日`，例如 12月4日。
    说明：这里严格按照 MASTER_WORKFLOW 中"美股封面日期=今天日期-1"的要求，
    不再直接使用 data_stock 里的 date_str，避免时差或缓存导致偏差。
    """
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%m月%d日")


def generate_stock_cover():
    print("📈 正在生成美股封面...")

    # 1. 背景处理
    bg_path = "assets/cover_stock_bg.png"
    # 如果没有专属背景，创建一个深蓝色的酷炫背景
    if os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        img = img.resize((CANVAS_WIDTH, CANVAS_HEIGHT))
    else:
        img = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (20, 25, 40))

    draw = ImageDraw.Draw(img)

    # 2. 绘制日期
    # 需求更新：封面日期固定为“今天日期-1”，例如在 12 月 5 日生成时显示“截止 12月4日 收盘”
    cn_date = get_yesterday_cn_date()
    full_date_text = f"截止 {cn_date} 收盘"

    font_size = 42  # ✅ 字号加大
    font = load_font(font_size)

    # 坐标：左 74, 顶 640 (只改变位置，其他不变)
    draw.text((74, 640), full_date_text, font=font, fill="#FFFFFF")

    # 3. 保存到专属文件夹
    output_dir = "stock_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, "cover_final.png")
    img.save(output_path)
    print(f"✅ 美股封面已生成: {output_path}")


if __name__ == "__main__":
    generate_stock_cover()