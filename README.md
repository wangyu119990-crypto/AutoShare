# AutoShare - 自媒体内容自动生成与发布工具

一个全自动化的自媒体内容生成系统，支持从数据抓取、图片生成到内容发布的全流程自动化。

> 🎯 **核心价值**：一键生成高质量图文内容，自动适配小红书等平台规范，让内容创作变得轻松高效。

## ✨ 功能特性

### 🟢 Product Hunt 榜单
- ✅ 自动抓取 Product Hunt 每日 Top 20 产品
- ✅ 智能中文翻译和内容格式化
- ✅ 自动生成精美封面和内容页图片（1245×1660 像素）
- ✅ 支持批量生成多页内容，智能排版

### 🔴 美股日报
- ✅ 自动获取美股科技股实时涨跌数据
- ✅ 可视化涨跌排行榜（红涨绿跌）
- ✅ 智能分页排版，自动避免孤儿页问题
- ✅ 支持价格变动详情展示

### 🔵 GitHub Trending
- ✅ 自动抓取 GitHub 每日热榜
- ✅ 智能识别新上榜项目
- ✅ 生成技术趋势分析图文
- ✅ 内容无害化处理，符合平台规范

### 🛡️ 安全机制
- ✅ 自动内容审查，符合小红书社区规范
- ✅ 敏感词汇过滤与无害化处理
- ✅ 数据来源验证与追踪
- ✅ 自动改写违规表述为安全内容

## 🛠️ 技术栈

- **Python 3.14+**
- **Playwright** - 浏览器自动化和截图
- **Jinja2** - HTML 模板引擎
- **Pillow (PIL)** - 图像处理
- **Markdown** - 内容格式化
- **Requests** - HTTP 请求

## 📦 安装依赖

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd AutoShare
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. 安装 Playwright 浏览器

```bash
playwright install chromium
```

## 🚀 快速开始

### 完整安装步骤

```bash
# 1. 克隆仓库
git clone <your-repo-url>
cd AutoShare

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 Playwright 浏览器
playwright install chromium
```

### 使用方法

#### 1. Product Hunt 榜单生成

```bash
python main.py
```

**输出结果**：
- `final_cover.png` - 封面图片
- `slide_*.png` - 内容页图片（多张）

#### 2. 美股日报生成

```bash
python main_stock.py
```

**输出结果**：
- `stock_output/cover_final.png` - 封面图片
- `stock_output/article_p*.png` - 内容页图片（多张）

#### 3. GitHub Trending 生成

```bash
python main_github.py
```

**输出结果**：
- `final_cover_github.png` - 封面图片
- `slide_*.png` - 内容页图片（多张）

#### 4. 一键生成所有内容

```bash
python run_all.py
```

这将依次执行所有三个任务，生成完整的图文素材。

## 📁 项目结构

```
AutoShare/
├── assets/                 # 模板资源（封面背景、字体）
│   ├── cover_bg.png       # PH 封面背景
│   ├── cover_template_github.png  # GitHub 封面背景
│   ├── stock_bg.png       # 美股封面背景
│   └── *.ttf, *.ttc       # 字体文件
├── templates/              # HTML 模板
│   ├── stock_cover.html   # 美股封面模板
│   └── stock_article.html # 美股文章模板
├── cover_template.html     # PH 封面模板
├── article_template.html   # PH 文章模板
├── main.py                 # PH 主程序
├── main_stock.py          # 美股主程序
├── main_github.py         # GitHub 主程序
├── gen_cover.py           # 封面生成器
├── gen_article.py         # 文章生成器
├── audit.py               # 内容审查
└── MASTER_WORKFLOW.md     # 详细使用文档
```

## ⚙️ 配置说明

### MCP 服务器配置

项目依赖以下 MCP 服务器进行数据获取和内容发布：

1. **ph-mcp-server** - 获取 Product Hunt 和 GitHub 数据
   - 用于抓取产品榜单和开源项目信息
   - 需要在 MCP 配置文件中配置服务器地址

2. **xiaohongshu-mcp** - 发布到小红书
   - 用于自动发布生成的内容
   - 需要配置登录状态和访问令牌

**配置示例**（根据你的 MCP 配置文件格式调整）：
```json
{
  "mcpServers": {
    "ph-mcp-server": {
      "url": "https://your-ph-mcp-server.com"
    },
    "xiaohongshu-mcp": {
      "url": "https://your-xhs-mcp-server.com"
    }
  }
}
```

### 图片尺寸标准

所有生成的图片统一尺寸：**1245×1660 像素**

- 尺寸配置在代码中统一管理，无需手动设置
- 自动适配小红书等平台的图片规格要求
- 支持高清输出，保证内容清晰度

## 📝 详细文档

完整的工作流程、数据格式说明和高级用法请参考：

👉 **[MASTER_WORKFLOW.md](./MASTER_WORKFLOW.md)** - 详细使用手册

该文档包含：
- 完整的工作流程说明
- 数据格式和变量结构
- 发布流程和参数配置
- 故障排查指南

## 🔒 安全提示

- ✅ 所有生成内容自动经过安全审查（`audit.py`）
- ✅ 敏感词汇会自动过滤和改写
- ✅ 自动适配平台内容规范
- ⚠️ 发布前建议人工复核关键内容

## ❓ 常见问题

### Q: 运行时提示找不到 Playwright 浏览器？
A: 请运行 `playwright install chromium` 安装浏览器驱动。

### Q: 图片生成失败怎么办？
A: 检查以下项：
- 模板文件是否存在（`assets/` 和 `templates/` 文件夹）
- 字体文件是否完整
- 磁盘空间是否充足

### Q: MCP 服务器连接失败？
A: 检查：
- MCP 服务器地址配置是否正确
- 网络连接是否正常
- 服务器是否可访问

### Q: 如何自定义图片样式？
A: 修改对应的 HTML 模板文件：
- PH 封面：`cover_template.html`
- PH 文章：`article_template.html`
- 美股封面：`templates/stock_cover.html`
- 美股文章：`templates/stock_article.html`

## 📄 许可证

本项目仅供学习和个人使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

- 🐛 发现问题？请提交 [Issue](../../issues)
- 💡 有改进建议？欢迎提交 [Pull Request](../../pulls)
- 📖 改进文档也是很好的贡献！

## 📮 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

---

⭐ 如果这个项目对你有帮助，欢迎 Star！

