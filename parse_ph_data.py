#!/usr/bin/env python3
"""
解析 ph-mcp-server 美股数据的脚本
"""

import json
import re

# ph-mcp-server 返回的数据
ph_data = {
    'trading_date': '2025-11-24',
    'news_count': 6,
    'news': [
        {
            'content': '📈 Alphabet Inc. 咔咔涨，一下 6.346%, 从 299.660 涨到 318.675\n📈 Meta Platforms, Inc. 咔咔涨，一下 3.207%, 从 594.250 涨到 613.310\n📈 Tesla, Inc. 咔咔涨，一下 6.753%, 从 391.090 涨到 417.500\n📈 Palantir Technologies Inc. 咔咔涨，一下 4.747%, 从 154.850 涨到 162.200\n📈 Snowflake Inc. 咔咔涨，一下 3.858%, 从 234.030 涨到 243.060\n📈 Fastly, Inc. 咔咔涨，一下 6.095%, 从 10.910 涨到 11.575\n📈 Cloudflare, Inc. 咔咔涨，一下 3.895%, 从 186.380 涨到 193.640\n📈 Pure Storage, Inc. 咔咔涨，一下 4.976%, 从 78.380 涨到 82.280\n📉 Rackspace Technology, Inc. 咔咔跌, 一下 5.213%, 从 1.055 跌到 1.000\n📈 JFrog Ltd. 咔咔涨，一下 3.141%, 从 59.220 涨到 61.080\n📈 CrowdStrike Holdings, Inc. 咔咔涨，一下 3.239%, 从 490.670 涨到 506.564'
        },
        {
            'content': '📈 Alphabet Inc. 咔咔涨，一下 3.527%, 从 289.450 涨到 299.660\n📉 Confluent, Inc. 咔咔跌, 一下 3.671%, 从 21.520 跌到 20.730\n📉 Elastic N.V. 咔咔跌, 一下 14.669%, 从 82.080 跌到 70.040\n📉 Oracle Corporation 咔咔跌, 一下 5.662%, 从 210.690 跌到 198.760\n📉 Snowflake Inc. 咔咔跌, 一下 4.345%, 从 244.660 跌到 234.030\n📈 Fastly, Inc. 咔咔涨，一下 3.510%, 从 10.540 涨到 10.910\n📈 NetApp, Inc. 咔咔涨，一下 3.933%, 从 103.240 涨到 107.300\n📈 Rackspace Technology, Inc. 咔咔涨，一下 4.455%, 从 1.010 涨到 1.055\n📈 F5, Inc. 咔咔涨，一下 3.746%, 从 225.830 涨到 234.290\n📈 Qualys, Inc. 咔咔涨，一下 3.749%, 从 137.900 涨到 143.070\n📈 Intuit Inc. 咔咔涨，一下 4.033%, 从 637.440 涨到 663.150\n📈 Workday, Inc. 咔咔涨，一下 3.842%, 从 216.810 涨到 225.140\n📈 The Trade Desk, Inc. 咔咔涨，一下 3.390%, 从 38.350 涨到 39.650\n📈 Box, Inc. 咔咔涨，一下 4.555%, 从 28.980 涨到 30.300\n📈 Docebo Inc. 咔咔涨，一下 3.174%, 从 20.480 涨到 21.130\n📈 Five9, Inc. 咔咔涨，一下 6.524%, 从 17.780 涨到 18.940\n📈 NICE Ltd. 咔咔涨，一下 5.532%, 从 99.600 涨到 105.110\n📈 Pegasystems Inc. 咔咔涨，一下 3.895%, 从 52.380 涨到 54.420\n📈 Similarweb Ltd. 咔咔涨，一下 4.178%, 从 7.180 涨到 7.480\n📈 Consensus Cloud Solutions, Inc. 咔咔涨，一下 3.557%, 从 20.240 涨到 20.960\n📈 Intapp, Inc. 咔咔涨，一下 3.694%, 从 40.070 涨到 41.550\n📉 Wix.com Ltd. 咔咔跌, 一下 3.981%, 从 99.470 跌到 95.510'
        }
    ]
}

def parse_stock_line(line):
    """解析股票数据行"""
    pattern = r'([📈📉])\s*(.+?)\s+咔咔(涨|跌).*?(\d+\.\d+)%.*?(\d+\.\d+)\s+(涨|跌)到\s+(\d+\.\d+)'
    match = re.search(pattern, line.strip())

    if match:
        direction, company, action, change_pct, old_price, action2, new_price = match.groups()
        change_pct = float(change_pct)
        old_price = float(old_price)
        new_price = float(new_price)

        if direction == '📉' or action == '跌':
            change_pct = -change_pct

        return {
            'company': company.strip(),
            'change_pct': change_pct,
            'old_price': old_price,
            'new_price': new_price
        }
    return None

def main():
    """主函数：解析并显示美股数据"""
    # 收集所有股票数据
    all_stocks = []

    for news_item in ph_data['news'][:2]:  # 只处理前两条最新的消息
        content = news_item['content']
        lines = content.split('\n')

        for line in lines:
            stock_info = parse_stock_line(line)
            if stock_info:
                # 检查是否已存在相同的公司（保留最新的数据）
                existing = next((s for s in all_stocks if s['company'] == stock_info['company']), None)
                if existing:
                    # 更新为更新的数据（通常是第一条消息中的）
                    if news_item == ph_data['news'][0]:  # 第一条消息优先
                        existing.update(stock_info)
                else:
                    all_stocks.append(stock_info)

    # 按涨跌幅排序
    up_stocks = sorted([s for s in all_stocks if s['change_pct'] > 0], key=lambda x: x['change_pct'], reverse=True)
    down_stocks = sorted([s for s in all_stocks if s['change_pct'] < 0], key=lambda x: x['change_pct'])

    print('📊 ph-mcp-server 最新美股数据 (2025年11月24日)')
    print('=' * 80)
    print('📈 涨幅最大的股票:')
    for i, stock in enumerate(up_stocks[:10], 1):
        print(f'{i:2d}. {stock["company"]:30} +{stock["change_pct"]:6.2f}%  ${stock["old_price"]:8.2f} → ${stock["new_price"]:8.2f}')

    print('\n📉 跌幅最大的股票:')
    for i, stock in enumerate(down_stocks[:5], 1):
        print(f'{i}. {stock["company"]:30} {stock["change_pct"]:6.2f}%  ${stock["old_price"]:8.2f} → ${stock["new_price"]:8.2f}')

    print(f'\n📋 数据统计:')
    print(f'   总计股票: {len(all_stocks)} 只')
    print(f'   上涨股票: {len(up_stocks)} 只')
    print(f'   下跌股票: {len(down_stocks)} 只')
    print(f'   数据来源: ph-mcp-server (实时获取)')

    # 保存解析后的数据
    parsed_data = {
        'trading_date': ph_data['trading_date'],
        'up_stocks': up_stocks,
        'down_stocks': down_stocks,
        'all_stocks': all_stocks
    }

    with open('ph_mcp_parsed_data.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, ensure_ascii=False, indent=2)

    print('💾 数据已保存到 ph_mcp_parsed_data.json')
if __name__ == "__main__":
    main()
