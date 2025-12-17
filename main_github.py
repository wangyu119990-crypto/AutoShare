import os
import glob
import subprocess
import requests
import re
import json
from datetime import datetime
from gen_cover_github import create_github_cover
from gen_article import create_smart_slides

# ================= 配置区域 =================
PH_MCP_URL = "https://phmcpserver-widgetinp950-8gga8iii.leapcell.dev/mcp"
PH_TOOL_NAME = "get_github_trending_report" 
# ===========================================

def get_absolute_path(filename):
    return os.path.join(os.getcwd(), filename)

def copy_to_clipboard(text):
    try:
        process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))
    except:
        pass

def fetch_data_from_leapcell():
    print("🕸️ 正在连接 MCP 服务器抓取数据...")
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": PH_TOOL_NAME, "arguments": {}},
        "id": 1
    }
    try:
        response = requests.post(PH_MCP_URL, json=payload, timeout=60)
        resp_json = response.json()
        if "result" in resp_json and "content" in resp_json["result"]:
            for item in resp_json["result"]["content"]:
                if item.get("type") == "text":
                    raw_text = item.get("text")
                    try:
                        inner_json = json.loads(raw_text)
                        if "markdown_content" in inner_json:
                            return inner_json["markdown_content"]
                    except:
                        return raw_text
        return None
    except Exception as e:
        print(f"❌ 数据抓取失败: {e}")
        return None

def parse_mcp_text(md_text):
    if not md_text: return [], {}, []
    md_text = md_text.replace("\\n", "\n")

    # 1. 新上榜
    new_names = []
    try:
        if "新上榜" in md_text:
            part1 = md_text.split("新上榜")[1]
            section = part1.split("跌出榜")[0] if "跌出榜" in part1 else part1.split("今日榜单")[0]
            matches = re.findall(r"-\s+#\d+\s+([^\n\r]+)", section)
            new_names = [m.strip() for m in matches]
    except: pass

    # 2. 详情
    all_details_map = {}
    simple_list_ordered = []
    if "今日榜单" in md_text:
        list_section = md_text.split("今日榜单")[1]
        chunks = list_section.split("### #")
        for chunk in chunks:
            if not chunk.strip(): continue
            lines = chunk.strip().split('\n')
            if not lines: continue
            parts = lines[0].strip().split(" ", 1)
            if len(parts) < 2: continue
            
            item = {"rank": parts[0].strip(), "name": parts[1].strip(), "stars": "N/A", "pr": "N/A", "lang": "Unknown", "desc": "暂无简介"}
            for line in lines[1:]:
                if "⭐" in line:
                    try:
                        s = line.split("|")
                        if len(s)>=1: item['stars'] = s[0].replace("⭐", "").strip()
                        if len(s)>=2: item['pr'] = s[1].replace("PR:", "").strip()
                        if len(s)>=3: item['lang'] = s[2].strip()
                    except: pass
                if "简介" in line:
                    item['desc'] = re.sub(r"\**简介\**:", "", line).strip()
            
            all_details_map[item['name']] = item
            simple_list_ordered.append(f"{item['rank']}. {item['name']}")

    return new_names, all_details_map, simple_list_ordered

def generate_smart_headline(new_names):
    if not new_names: return "GitHub 热榜\n全球开发者关注的开源趋势"
    short_names = [n.split('/')[-1] for n in new_names[:3]]
    names_str = "、".join(short_names[:-1]) + "和" + short_names[-1] if len(short_names) > 1 else short_names[0]
    return f"{names_str}强势上榜，\n引领今日开源技术新关注。"

def format_slides_content(new_names, all_details_map):
    text = ""
    count = 0
    added = set()
    for name in new_names:
        target = all_details_map.get(name)
        if not target:
            for k, v in all_details_map.items():
                if name.lower() == k.lower():
                    target = v; break
        
        if target and target['name'] not in added:
            text += f"## {target['rank']}. {target['name']}\n"
            text += f"**⭐ {target['stars']} | PR: {target['pr']} | 语言: {target['lang']}**\n"
            text += f"> 简介：{target['desc']}\n\n"
            added.add(target['name'])
            count += 1
    return text, count

def run_github_automation():
    print("🚀 AutoShare: GitHub Trending 自动发布任务启动")
    
    # 1. 抓取与解析
    raw_md = fetch_data_from_leapcell()
    if not raw_md: return
    new_names, all_details_map, simple_list_ordered = parse_mcp_text(raw_md)
    
    if not new_names:
        print("🛑 今日无新上榜产品，跳过。")
        return
        
    print(f"📊 发现 {len(new_names)} 个新产品，准备生成素材...")

    # 2. 生成图片
    today_date = datetime.now().strftime("%Y.%m.%d")
    today_date_cn = datetime.now().strftime("%Y年%m月%d日")
    
    headline = generate_smart_headline(new_names)
    cover_path = get_absolute_path(create_github_cover(today_date, headline))
    
    article_formatted, count = format_slides_content(new_names, all_details_map)
    if count == 0:
        print("🛑 无法匹配详细信息，终止。")
        return
        
    for f in glob.glob("slide_*.png"): os.remove(f)
    create_smart_slides(f"GitHub Trending 新上榜 - {today_date_cn}", article_formatted)
    
    slides = sorted(glob.glob("slide_*.png"), key=lambda x: int(x.split('_')[1].split('.')[0]))
    slide_paths = [get_absolute_path(s) for s in slides]
    all_images = [cover_path] + slide_paths
    
    # 3. 准备发布内容
    final_title = f"【GitHubTrending 热榜】{today_date_cn}"
    simple_list_text = "\n".join(simple_list_ordered)
    full_body = f"今日总榜\n{simple_list_text}"
    tags = "#githubtrending #ai #ai工具 #AIGC #开发者选项 #算法 #自动化 #工作流 #转码 #开发"

    # 4. 生成指令文本 (供 Agent 读取)
    # 我们把图片路径列表转成 JSON 格式的字符串，方便 Agent 识别
    mcp_instruction = {
        "action": "publish_content",
        "title": final_title,
        "content": full_body + "\n\n" + tags,
        "images": all_images
    }
    
    print("\n" + "="*20 + " 任务完成：请 Agent 执行以下指令 " + "="*20)
    # 这里直接打印出结构化的 JSON，方便 AI 读取
    print(json.dumps(mcp_instruction, indent=2, ensure_ascii=False))
    print("="*50)
    
    # 同时复制一段可读性强的到剪贴板，给人看
    human_cmd = f"发布小红书 标题={final_title} 正文=... 图片数={len(all_images)}"
    copy_to_clipboard(human_cmd)

    os.system(f"open {os.getcwd()}")

if __name__ == "__main__":
    run_github_automation()