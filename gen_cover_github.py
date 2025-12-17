import os
from jinja2 import Template
from playwright.sync_api import sync_playwright

# 你的封面配置参数 (严格按照要求)
COVER_CONFIG = {
    # ⚠️ 修正点：指向 assets 文件夹
    "bg_image": "assets/cover_template_github.png", 
    "date": {
        "x": "105px",
        "y": "460px",
        "font": "Century Gothic",
        "weight": "bold",
        "size": "45px",
        "color": "#ffffff"
    },
    "headline": {
        "x": "105px",
        "y": "539px",
        "font": "PingFang SC",
        "weight": "500", 
        "size": "30px",
        "line_height": "145%",
        "spacing": "0.02em", 
        "color": "#ffffff"
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; width: 1245px; height: 1660px; overflow: hidden; }
        .container {
            position: relative;
            width: 1245px;
            height: 1660px;
            background-image: url('{{ bg_image }}');
            background-size: cover;
        }
        .date-text {
            position: absolute;
            left: {{ c.date.x }};
            top: {{ c.date.y }};
            font-family: '{{ c.date.font }}', sans-serif;
            font-weight: {{ c.date.weight }};
            font-size: {{ c.date.size }};
            color: {{ c.date.color }};
            z-index: 10;
        }
        .headline-text {
            position: absolute;
            left: {{ c.headline.x }};
            top: {{ c.headline.y }};
            width: 900px; /* 限制宽度防止溢出 */
            font-family: '{{ c.headline.font }}', sans-serif;
            font-weight: {{ c.headline.weight }};
            font-size: {{ c.headline.size }};
            line-height: {{ c.headline.line_height }};
            letter-spacing: {{ c.headline.spacing }};
            color: {{ c.headline.color }};
            white-space: pre-wrap;
            z-index: 10;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="date-text">{{ date_str }}</div>
        <div class="headline-text">{{ headline_str }}</div>
    </div>
</body>
</html>
"""

def create_github_cover(date_str, headline_str):
    print(f"🎨 [GitHub] 正在生成封面：日期={date_str}...")
    current_dir = os.getcwd()
    
    # 渲染 HTML
    template = Template(HTML_TEMPLATE)
    html_rendered = template.render(
        bg_image=COVER_CONFIG["bg_image"],
        c=COVER_CONFIG,
        date_str=date_str,
        headline_str=headline_str
    )
    
    temp_html_path = os.path.join(current_dir, "temp_github_cover.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_rendered)
        
    # 截图
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # 视口大小必须与封面尺寸一致
        page = browser.new_page(viewport={'width': 1245, 'height': 1660})
        page.goto(f"file://{temp_html_path}")
        
        output_filename = "final_cover_github.png"
        page.screenshot(path=output_filename)
        
        browser.close()
        
    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)
        
    print(f"✅ GitHub 封面已保存：{output_filename}")
    return output_filename