import requests
import json

XHS_MCP_URL = "http://localhost:18060/mcp"

print("🔍 正在检查小红书发布工具的详细参数...")

payload = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
}

try:
    response = requests.post(XHS_MCP_URL, json=payload, timeout=5)
    data = response.json()
    
    if "result" in data and "tools" in data["result"]:
        for tool in data["result"]["tools"]:
            if tool['name'] == "publish_content": # 或者是 publish_note
                print(f"\n✅ 找到了工具: {tool['name']}")
                print("📝 它支持的参数有：")
                props = tool['inputSchema']['properties']
                for key, value in props.items():
                    print(f"   - {key}: {value.get('description', '无描述')}")
                
                if "topics" in props:
                    print("\n🎉 发现 'topics' 参数！我们需要用这个！")
                else:
                    print("\n⚠️ 没发现 'topics' 参数，可能需要改用 #关键词[话题]# 格式。")
                break
    else:
        print("❌ 没获取到工具列表")

except Exception as e:
    print(f"❌ 连接失败: {e}")