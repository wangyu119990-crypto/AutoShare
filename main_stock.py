import os
import sys
import subprocess
import importlib
from datetime import datetime

# ==========================================
# 🛑 核心逻辑 1：美股休市自动检查
# ==========================================
def check_market_status():
    """
    检查今天是否为美股休市对应的亚洲时间。
    美股周六/周日休市 -> 对应亚洲时间 周日/周一。
    """
    # weekday(): 0=周一, 6=周日
    today_weekday = datetime.now().weekday()
    
    if today_weekday == 6 or today_weekday == 0:
        print("\n" + "="*40)
        print("💤 检测到今天是亚洲时间 周日/周一")
        print("💤 对应美股周末休市，无新数据。")
        print("💤 任务自动跳过！")
        print("="*40 + "\n")
        sys.exit(0) # 正常退出，不报错

# ==========================================
# 🔄 核心逻辑 2：数据获取与生成
# ==========================================
def run_stock_automation():
    # 1. 先检查是否休市
    check_market_status()

    print("🚀 开始执行美股日报任务...")

    # 2. 强制获取最新数据 (调用 fetch_stock_data.py)
    print("📡 正在从 MCP 服务器抓取最新美股数据...")
    try:
        # 这一步会重写 data_stock.py
        subprocess.run(["python3", "fetch_stock_data.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ 数据获取失败，终止任务")
        sys.exit(1)

    # 3. 动态重新加载数据 (防止缓存)
    try:
        import data_stock
        importlib.reload(data_stock) # 强制刷新，确保读到刚写入的数据
        print(f"📅 获取数据日期：{data_stock.date_str}")

        # 验证数据结构完整性
        required_attrs = ['stock_list_text', 'stock_content_formatted', 'TOPICS', 'date_str', 'stock_data']
        missing_attrs = [attr for attr in required_attrs if not hasattr(data_stock, attr)]
        if missing_attrs:
            print(f"❌ data_stock.py 缺少必要属性: {missing_attrs}")
            sys.exit(1)

        print("✅ 数据结构验证通过")
    except ImportError:
        print("❌ 找不到 data_stock.py，请检查数据获取步骤")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        sys.exit(1)

    # 4. 生成封面
    print("🎨 正在生成美股封面...")
    try:
        from gen_cover_stock import generate_stock_cover
        # 直接调用封面生成函数
        generate_stock_cover()
    except Exception as e:
        print(f"⚠️ 封面生成出错: {e}")
        # 如果不知道具体参数，可以根据你的 gen_cover_stock.py 自行调整

    # 5. 生成长图
    print("🎨 正在生成美股长图...")
    try:
        # 调用 gen_stock_pw.py (Playwright 生成器)
        # 假设该文件可以直接运行，或者有一个 run/create 函数
        # 这里使用 subprocess 直接调用文件最稳妥，避免函数名猜错
        subprocess.run(["python3", "gen_stock_pw.py"], check=True)
    except Exception as e:
        print(f"❌ 长图生成失败: {e}")
        sys.exit(1)

    # 6. 成功提示
    print("\n" + "="*40)
    print("✅ 美股图片生成完毕！保存在 stock_output 文件夹")
    print("="*40 + "\n")

    # 打开文件夹方便查看
    cwd = os.getcwd()
    try:
        os.system(f"open {os.path.join(cwd, 'stock_output')}")
    except:
        pass

if __name__ == "__main__":
    run_stock_automation()