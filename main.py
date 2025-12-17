import os
import glob
import subprocess
import data
from datetime import datetime # 引入时间模块
from gen_cover import create_cover
from gen_article import create_smart_slides
from audit import perform_content_audit

def get_absolute_path(filename):
    return os.path.join(os.getcwd(), filename)

def copy_to_clipboard(text):
    try:
        process = subprocess.Popen(
            'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE
        )
        process.communicate(text.encode('utf-8'))
    except Exception as e:
        print(f"⚠️ 剪贴板复制失败 (可能是非Mac系统): {e}")

def run_automation():
    # 安全审查：检查内容是否符合小红书规范
    perform_content_audit()

    print("🚀 开始执行 PH 榜单生成任务...")
    
    # --- 核心修改：获取电脑系统的真实日期 ---
    # 格式：2025.11.22
    today_date = datetime.now().strftime("%Y.%m.%d")
    # 格式：2025年11月22日 (用于标题)
    today_date_cn = datetime.now().strftime("%Y年%m月%d日")
    
    print(f"📅 锁定今日日期：{today_date}")
    
    # 1. 生成封面
    # 强制使用系统日期，无视 data.py 里的旧日期
    create_cover(today_date, data.cover_data["summary"])
    cover_path = get_absolute_path("final_cover.png")
    
    # 2. 生成长图
    for f in glob.glob("slide_*.png"):
        os.remove(f)
    
    # 确保长图标题的日期也自动更新
    real_title = data.article_title
    if "202" in real_title: 
        real_title = f"Product Hunt 每日排行榜 - {today_date_cn}"
        
    # 注意：这里使用 data.article_content_formatted 生成图片，图片里要有详细内容
    create_smart_slides(real_title, data.article_content_formatted)
    
    # 排序图片
    slides = sorted(glob.glob("slide_*.png"), key=lambda x: int(x.split('_')[1].split('.')[0]))
    slide_paths = [get_absolute_path(s) for s in slides]
    
    # 3. 拼装发布信息
    all_images = [cover_path] + slide_paths
    images_str = " ".join(f'"{img}"' for img in all_images)
    
    # --- 关键修改：正文只保留榜单列表，去掉详细长文，符合小红书字数限制 ---
    # 格式严格按照你的要求：今日榜单（总榜）\n今日总榜（总榜前 20）...
    full_body = f"今日榜单（总榜）\n\n{data.simple_list_text}"

    # 4. 拼装 MCP 指令 - 恢复长标题
    final_title = f"Product Hunt 每日排行榜 - {today_date_cn}"

    # 修改前（容易出错）：
    # tag=#产品[话题]# #ai[话题]# #agent[话题]# ...
    
    # 修改后（更稳定）：
    # 只写关键词，让 MCP 自动去联想匹配
    mcp_command = f"""
发布小红书笔记，标题={final_title} 正文={full_body}
tag=#产品 #AI #Agent #排行榜 #效率工具 #独立开发 #数据 #科技 添加合集=Product Hunt 每日热榜 配图={images_str}
    """
    
    print("\n" + "="*20 + " MCP 调用指令 " + "="*20)
    print(mcp_command.strip())
    print("="*50)
    
    copy_to_clipboard(mcp_command.strip())
    print("📋 指令已复制到剪贴板！")
    
    # 打开文件夹
    cwd = os.getcwd()
    os.system(f"open {cwd}")

if __name__ == "__main__":
    run_automation()