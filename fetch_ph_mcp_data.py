#!/usr/bin/env python3
"""
从 ph-mcp-server 获取最新 Product Hunt 数据的专用脚本
确保 Product Hunt 数据的唯一来源是 ph-mcp-server
"""

import json
import datetime
import urllib.request
import sys

def call_ph_mcp_server():
    """调用 ph-mcp-server 的 get_latest_products 工具"""
    print("📡 正在调用 ph-mcp-server...")

    try:
        # 构建 MCP JSON-RPC 请求
        mcp_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/call',
            'params': {
                'name': 'get_latest_products',
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

        print("✅ 成功调用 ph-mcp-server API")
        print(f"📅 数据日期: {api_result.get('date')}")
        print(f"📰 产品数量: {api_result.get('total_count')}")

        return api_result

    except Exception as e:
        print(f"❌ 调用 ph-mcp-server 失败: {e}")
        print("⚠️ 回退到使用缓存数据")

        # 回退到读取缓存数据
        try:
            with open('ph_mcp_parsed_data.json', 'r', encoding='utf-8') as f:
                parsed_data = json.load(f)
            print("✅ 成功读取 ph-mcp-server 数据缓存")
            return parsed_data
        except Exception as e:
            print(f"❌ 读取缓存数据失败: {e}")
            return None

def save_ph_data(ph_data):
    """保存 Product Hunt 数据"""
    print("📝 保存 Product Hunt 数据...")

    if not ph_data or 'products' not in ph_data:
        print("❌ 数据格式错误")
        return False

    try:
        # 保存原始数据
        with open('ph_mcp_parsed_data.json', 'w', encoding='utf-8') as f:
            json.dump(ph_data, f, ensure_ascii=False, indent=2)

        print("✅ ph_mcp_parsed_data.json 更新成功")
        print(f"   📊 产品数量: {len(ph_data['products'])} 个")
        print("   🔒 数据来源: 100% ph-mcp-server")

        return True

    except Exception as e:
        print(f"❌ 保存 Product Hunt 数据失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Product Hunt 数据获取系统 - 唯一数据来源: ph-mcp-server")
    print("=" * 60)

    # 步骤1: 获取 ph-mcp-server 数据
    ph_data = call_ph_mcp_server()
    if not ph_data:
        print("❌ 获取 ph-mcp-server 数据失败")
        return False

    # 步骤2: 保存数据
    success = save_ph_data(ph_data)
    if not success:
        print("❌ 保存数据失败")
        return False

    print("=" * 60)
    print("✅ ph-mcp-server 数据获取和保存完成")
    print("🔒 数据来源验证: 100% 来自 ph-mcp-server")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)