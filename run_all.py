import os
import sys

def run_generation():
    print("\n" + "="*40)
    print("🏭 工厂启动：开始生成图片素材...")
    print("="*40 + "\n")

    # 1. 生成 Product Hunt 图片
    print("📦 [1/2] 正在执行 PH 生成脚本...")
    exit_code_ph = os.system("python main.py")
    if exit_code_ph != 0:
        print("❌ PH 生成失败！")
        sys.exit(1)

    print("\n" + "-"*20 + "\n")

    # 2. 生成 美股日报 图片
    print("📈 [2/2] 正在执行 美股 生成脚本...")
    exit_code_stock = os.system("python main_stock.py")
    if exit_code_stock != 0:
        print("❌ 美股 生成失败！")
        sys.exit(1)

    print("\n" + "="*40)
    print("✅ 素材生产完成！准备移交发布 MCP...")
    print("="*40 + "\n")

if __name__ == "__main__":
    run_generation()