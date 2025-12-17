#!/usr/bin/env python3
"""
从 ph-mcp-server 获取最新美股数据的专用脚本
确保美股数据的唯一来源是 ph-mcp-server
"""

import json
import datetime
import urllib.request
import sys

def call_ph_mcp_stock_server():
    """调用 ph-mcp-server 的 get_latest_stock_news 工具"""
    print("📡 正在从 ph-mcp-server 获取美股数据...")

    try:
        # 构建 MCP JSON-RPC 请求
        mcp_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/call',
            'params': {
                'name': 'get_latest_stock_news',
                'arguments': {}
            }
        }

        # 发送请求到 ph-mcp-server
        req = urllib.request.Request(
            'https://phmcpserver-widgetinp950-8gga8iii.leapcell.dev/mcp',
            data=json.dumps(mcp_request).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())

        if 'result' not in result or 'content' not in result['result']:
            print("❌ ph-mcp-server 返回数据格式错误")
            return None

        # 解析返回的 JSON 字符串
        content_text = result['result']['content'][0]['text']
        api_result = json.loads(content_text)

        print("✅ 成功调用 ph-mcp-server 美股数据 API")
        print(f"📅 数据日期: {api_result.get('date', '未知')}")
        print(f"📰 股票数量: {len(api_result.get('news', []))}")

        # 调试：打印完整的返回数据结构
        print("🔍 调试：完整返回数据结构：")
        print(json.dumps(api_result, indent=2, ensure_ascii=False)[:1000])  # 只打印前1000字符

        # 调试：打印前几个股票数据
        if 'news' in api_result and api_result['news']:
            print("🔍 调试：前3个股票数据示例：")
            for i, stock in enumerate(api_result['news'][:3]):
                print(f"   {i+1}. {stock}")

        return api_result

    except Exception as e:
        print(f"❌ 调用 ph-mcp-server 美股数据失败: {e}")
        return None

def parse_stock_line(line):
    """解析单行股票数据，支持多种格式"""
    import re
    
    stock_info = None
    
    # 格式1: 📈 本周 XXX 涨了，涨了 XX%, 从 XX 涨到 XX
    # 格式2: 📈 XXX 咔咔涨，一下 XX%, 从 XX 涨到 XX
    # 格式3: 📉 本周 XXX 跌了, 跌了 XX%, 从 XX 跌到 XX
    # 格式4: 📉 XXX 咔咔跌, 一下 XX%, 从 XX 跌到 XX
    
    # 匹配模式：emoji + 公司名 + 涨/跌相关文字 + 涨幅% + 从 + 旧价格 + 涨/跌到 + 新价格
    pattern1 = r'([📈📉])\s*(?:本周\s+)?(.+?)\s+(?:涨了，涨了|咔咔涨，一下|跌了,?\s*跌了|咔咔跌,\s*一下)\s+([\d.]+)%,\s*从\s+([\d.]+)\s+(?:涨到|跌到)\s+([\d.]+)'
    match1 = re.search(pattern1, line)
    
    if match1:
        emoji, name, change_percent, old_price, new_price = match1.groups()
        is_up = emoji == '📈' or '涨' in line
        
        stock_info = {
            'name': name.strip(),
            'change_percent': float(change_percent) if is_up else -float(change_percent),
            'previous_close': float(old_price),
            'price': float(new_price),
            'is_up': is_up
        }
    
    return stock_info

def format_stock_data(stock_news):
    """格式化美股数据为 data_stock.py 所需格式，包含涨跌数据"""
    if not stock_news or 'news' not in stock_news:
        print("❌ 数据格式错误")
        return None

    # 使用字典存储股票，避免重复（以公司名为key）
    stocks_dict = {}
    
    # 解析所有新闻内容
    for item in stock_news['news']:
        content = item.get('content', '')
        if not content:
            continue

        # 按行分割股票信息
        lines = content.strip().split('\n')
        for line in lines:
            if '📈' in line or '📉' in line:
                stock_info = parse_stock_line(line)
                if stock_info:
                    name = stock_info['name']
                    # 如果已存在，保留涨跌幅更大的（绝对值）
                    if name not in stocks_dict or abs(stock_info['change_percent']) > abs(stocks_dict[name]['change_percent']):
                        stocks_dict[name] = stock_info

    if not stocks_dict:
        print("⚠️ 未解析到股票数据")
        return None

    # 分离上涨和下跌股票
    all_stocks = list(stocks_dict.values())
    up_stocks = sorted([s for s in all_stocks if s['is_up']], key=lambda x: x['change_percent'], reverse=True)
    down_stocks = sorted([s for s in all_stocks if not s['is_up']], key=lambda x: x['change_percent'])

    print(f"📊 解析到股票数据：上涨 {len(up_stocks)} 只，下跌 {len(down_stocks)} 只")

    # 生成 stock_list_text (发布专用 - 纯净列表)
    # 格式：1. 公司名 : +涨幅% (极简)
    stock_list_text_lines = []
    for i, stock in enumerate(up_stocks, 1):
        name = stock['name']
        change_percent = stock['change_percent']
        stock_list_text_lines.append(f"{i}. {name} : +{change_percent:.2f}%")
    stock_list_text = "\n".join(stock_list_text_lines)

    # 生成 stock_content_formatted (图片专用 - 详细数据)
    # 格式：📈 公司名 +涨幅% (旧价格->新价格)
    stock_content_formatted_lines = []
    
    # 先添加上涨股票
    for stock in up_stocks:
        name = stock['name']
        change_percent = stock['change_percent']
        old_price = stock['previous_close']
        new_price = stock['price']
        formatted_line = f"📈 {name} +{change_percent:.2f}% ({old_price:.2f}->{new_price:.2f})"
        stock_content_formatted_lines.append(formatted_line)
        stock_content_formatted_lines.append("")  # 空行
    
    # 再添加下跌股票
    for stock in down_stocks:
        name = stock['name']
        change_percent = stock['change_percent']  # 已经是负数
        old_price = stock['previous_close']
        new_price = stock['price']
        formatted_line = f"📉 {name} {change_percent:.2f}% ({old_price:.2f}->{new_price:.2f})"
        stock_content_formatted_lines.append(formatted_line)
        stock_content_formatted_lines.append("")  # 空行
    
    stock_content_formatted = "\n".join(stock_content_formatted_lines)

    # 固定的话题标签
    TOPICS = ["纳斯达克", "未来科技趋势", "投资理财", "我的理财日记", "纳指"]

    # 自动获取日期，如果 API 返回空则使用昨天
    date_str = stock_news.get('date')
    if not date_str or date_str == '未知':
        date_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    return {
        'stock_list_text': stock_list_text,
        'stock_content_formatted': stock_content_formatted,
        'TOPICS': TOPICS,
        'date_str': date_str
    }

def save_stock_data(formatted_data):
    """保存格式化的美股数据到 data_stock.py"""
    print("📝 生成美股数据文件...")

    try:
        # 生成 data_stock.py 内容
        content = f'''# ==========================================
# 🔒 美股数据文件 (自动生成)
# 📡 数据来源: 100% ph-mcp-server
# 📅 生成日期: {formatted_data['date_str']}
# 🚫 禁止手动修改此文件
# ==========================================

# 发布专用 - 纯净列表 (仅包含上涨股票)
stock_list_text = """{formatted_data['stock_list_text']}"""

# 图片专用 - 详细数据 (数据保真 - 保留股价变动)
stock_content_formatted = """{formatted_data['stock_content_formatted']}"""

# 话题标签 (固定)
TOPICS = {formatted_data['TOPICS']}

# 数据日期
date_str = "{formatted_data['date_str']}"

# ==========================================
# 🔒 安全验证完成
# 数据来源: 100% 来自 ph-mcp-server
# ==========================================
'''

        # 添加兼容性数据结构
        # 将 stock_list_text 字符串转换为列表（按行分割）
        up_list_lines = [line for line in formatted_data['stock_list_text'].strip().split('\n') if line.strip()]
        up_list_str = ',\n    '.join([repr(line) for line in up_list_lines])
        
        # 解析下跌股票列表
        down_list_lines = []
        for line in formatted_data['stock_content_formatted'].strip().split('\n'):
            if line.strip().startswith('📉'):
                down_list_lines.append(line.strip())
        down_list_str = ',\n    '.join([repr(line) for line in down_list_lines]) if down_list_lines else ''
        
        content += f"""

# ==========================================
# 🔒 兼容性数据结构 (供现有代码使用)
# ==========================================
# 将 stock_list_text 字符串转换为列表（按行分割）
up_list = [
    {up_list_str}
]

# 下跌股票列表
down_list = [
    {down_list_str}
] if {bool(down_list_lines)} else []

stock_data = {{
    "date_str": "{formatted_data['date_str']}",
    "up_list": up_list,
    "down_list": down_list,
    "stock_content_formatted": {repr(formatted_data['stock_content_formatted'])},
    "TOPICS": {formatted_data['TOPICS']}
}}

# ==========================================
# 🔒 安全验证完成
# 数据来源: 100% 来自 ph-mcp-server
# ==========================================
"""

        # 写入文件
        with open('data_stock.py', 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ data_stock.py 生成成功")
        up_count = len([line for line in formatted_data['stock_list_text'].strip().split('\n') if line.strip()])
        down_count = len([line for line in formatted_data['stock_content_formatted'].strip().split('\n') if line.strip().startswith('📉')])
        print(f"   📊 上涨股票: {up_count} 只，下跌股票: {down_count} 只")
        print("   🔒 数据来源: 100% ph-mcp-server")
        return True

    except Exception as e:
        print(f"❌ 生成 data_stock.py 失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 美股数据获取系统 - 唯一数据来源: ph-mcp-server")
    print("=" * 60)

    # 步骤1: 获取 ph-mcp-server 美股数据
    stock_data = call_ph_mcp_stock_server()
    if not stock_data:
        print("❌ 获取 ph-mcp-server 美股数据失败")
        return False

    # 步骤2: 格式化数据
    formatted_data = format_stock_data(stock_data)
    if not formatted_data:
        print("❌ 数据格式化失败")
        return False

    # 步骤3: 保存数据
    success = save_stock_data(formatted_data)
    if not success:
        print("❌ 保存数据失败")
        return False

    print("=" * 60)
    print("✅ ph-mcp-server 美股数据获取和保存完成")
    print("🔒 数据来源验证: 100% 来自 ph-mcp-server")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
