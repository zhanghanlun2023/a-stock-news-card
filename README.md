# A股每日新闻卡片 📰

> 自动抓取沪深市场资讯、指数行情、热搜板块，生成精美Streamlit新闻仪表板

[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)

---

## 功能特性

| 模块 | 说明 |
|------|------|
| 📊 **三大指数** | 上证指数/深证成指/创业板指实时行情 |
| 📰 **财经新闻** | 东方财富新闻自动筛选，按政策/行业/个股/国际分类 |
| 🔥 **热搜股票** | 东方财富热搜排行 TOP8 |
| 📈 **热门板块** | 概念板块涨跌幅排行 TOP10 |
| 📅 **交易日历** | 自动识别交易日/休市状态 |
| 🔄 **自动刷新** | 每10分钟自动刷新数据 |

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 部署到 Streamlit Cloud

1. Fork 本仓库
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 点击 **New app** → 选择本仓库
4. Main file path: `app.py`
5. 点击 **Deploy!**

部署后访问: `https://a-stock-news-card.streamlit.app`

## 每日更新机制

- 数据通过 AKShare 实时抓取东方财富 API
- Streamlit `@st.cache_data` 缓存策略：指数5分钟、新闻/热搜10分钟刷新
- 前端每10分钟自动刷新页面
- 每次用户访问时自动拉取最新数据

## 项目结构

```
a-stock-news-card/
├── app.py              # Streamlit主应用
├── requirements.txt    # Python依赖
├── .streamlit/
│   └── config.toml    # Streamlit配置（主题、服务器）
└── utils/
    └── data_fetcher.py # 数据采集模块（AKShare API封装）
```

## 数据来源

- 东方财富 (EastMoney) 公开数据接口
- 通过 [AKShare](https://github.com/akfamily/akshare) 开源库获取
