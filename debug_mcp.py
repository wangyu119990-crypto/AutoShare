import requests
import json

# 你的 MCP 服务器地址
url = "https://phmcpserver-widgetinp950-8gga8iii.leapcell.dev/mcp"

print("🔍 正在询问服务器有哪些工具 (tools/list)...")

payload = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
}

try:
    response = requests.post(url, json=payload, timeout=10)
    data = response.json()
    
    if "result" in data and "tools" in data["result"]:
        tools = data["result"]["tools"]
        print(f"✅ 成功连接！服务器包含 {len(tools)} 个工具：")
        for t in tools:
            print(f"👉 工具名称 (Name): {t['name']}")
            print(f"   描述: {t.get('description', '无描述')}")
            print("-" * 30)
            
        print("\n请把上面的【工具名称】填入 main_github.py 的 TOOL_NAME 变量中！")
    else:
        print("❌ 服务器返回了奇怪的数据：")
        print(json.dumps(data, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"❌ 连接失败: {e}")