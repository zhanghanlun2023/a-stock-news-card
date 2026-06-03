"""
A股数据采集模块
使用 akshare 获取指数行情、财经新闻、热搜股票、热门板块、投资日历
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import streamlit as st


# ── 核心关键词（用于新闻筛选打分）─────────────────────────────
P0_KEYWORDS = ["重磅", "突发", "紧急", "重大", "历史性"]
P1_KEYWORDS = ["政策", "央行", "证监会", "国务院", "发改委", "财政部", "降准", "降息", "加息"]
P2_KEYWORDS = ["涨停", "跌停", "涨超", "跌超", "暴涨", "暴跌", "业绩", "分红", "回购", "减持"]
P3_KEYWORDS = ["突破", "创新高", "创新低", "反弹", "反转", "利好", "利空", "制裁"]
P4_KEYWORDS = ["半导体", "AI", "人工智能", "芯片", "新能源", "光伏", "锂电池", "算力",
               "机器人", "自动驾驶", "存储", "光模块", "CPO", "HBM", "大模型",
               "医药", "军工", "消费", "房地产", "电力", "煤炭", "石油"]


def score_news(title: str) -> int:
    """根据标题关键词打分"""
    score = 0
    for kw in P0_KEYWORDS:
        if kw in title:
            score += 5
    for kw in P1_KEYWORDS:
        if kw in title:
            score += 4
    for kw in P2_KEYWORDS:
        if kw in title:
            score += 3
    for kw in P3_KEYWORDS:
        if kw in title:
            score += 2
    for kw in P4_KEYWORDS:
        if kw in title:
            score += 1
    return score


def classify_news(title: str) -> str:
    """新闻分类"""
    policy_kw = ["政策", "央行", "证监会", "国务院", "发改委", "财政部", "降准", "降息",
                 "监管", "法规", "政治局", "常委会", "国常会", "中央", "政府", "部门"]
    industry_kw = ["半导体", "AI", "人工智能", "芯片", "新能源", "光伏", "锂电池", "算力",
                   "机器人", "自动驾驶", "存储", "光模块", "医药", "军工", "消费", "汽车",
                   "电力", "煤炭", "石油", "钢铁", "化工", "互联网", "5G", "通信"]
    intl_kw = ["美联储", "美股", "港股", "日经", "欧洲", "原油", "黄金", "美元", "汇率",
               "WTO", "IMF", "贸易战", "制裁", "地缘"]

    if any(kw in title for kw in policy_kw):
        return "政策要闻"
    elif any(kw in title for kw in intl_kw):
        return "国际市场"
    elif any(kw in title for kw in industry_kw):
        return "行业动态"
    else:
        return "个股异动"


# ── 指数行情 ─────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_index_quotes() -> list:
    """获取三大指数实时行情"""
    try:
        import akshare as ak
        df = ak.stock_zh_index_spot_em()
        # 筛选三大指数
        targets = {
            "上证指数": "000001",
            "深证成指": "399001",
            "创业板指": "399006",
        }
        results = []
        for name, code in targets.items():
            row = df[df["代码"] == code]
            if not row.empty:
                r = row.iloc[0]
                results.append({
                    "name": name,
                    "code": code,
                    "price": float(r["最新价"]),
                    "change_pct": float(r["涨跌幅"]),
                    "change_amt": float(r["涨跌额"]),
                    "volume": float(r.get("成交额", 0)) / 1e8,  # 转为亿
                })
        return results
    except Exception as e:
        st.warning(f"指数数据获取失败: {e}")
        # 返回默认占位数据
        return [
            {"name": "上证指数", "code": "000001", "price": 0, "change_pct": 0, "change_amt": 0, "volume": 0},
            {"name": "深证成指", "code": "399001", "price": 0, "change_pct": 0, "change_amt": 0, "volume": 0},
            {"name": "创业板指", "code": "399006", "price": 0, "change_pct": 0, "change_amt": 0, "volume": 0},
        ]


# ── 财经新闻 ─────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_news(max_news: int = 15) -> list:
    """获取东方财富财经新闻，筛选重大新闻"""
    try:
        import akshare as ak
        df = ak.stock_news_em()
        if df is None or df.empty:
            return _fallback_news()

        news_list = []
        for _, row in df.iterrows():
            title = str(row.get("标题", "")).strip()
            if not title or len(title) < 6:
                continue
            score = score_news(title)
            category = classify_news(title)
            news_list.append({
                "title": title,
                "content": str(row.get("内容", ""))[:120].strip(),
                "source": str(row.get("来源", "东方财富")).strip(),
                "time": str(row.get("发布时间", "")).strip(),
                "url": str(row.get("新闻链接", "")).strip(),
                "score": score,
                "category": category,
            })

        # 按分数排序，取前N条
        news_list.sort(key=lambda x: x["score"], reverse=True)
        return news_list[:max_news]
    except Exception as e:
        st.warning(f"新闻数据获取失败: {e}")
        return _fallback_news()


def _fallback_news() -> list:
    """备用新闻数据"""
    today = datetime.now().strftime("%m-%d")
    return [
        {"title": "（数据加载中，请稍后刷新页面）", "content": "", "source": "系统",
         "time": today, "url": "", "score": 0, "category": "系统提示"},
    ]


# ── 热搜股票 ─────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_hot_stocks(top_n: int = 8) -> list:
    """获取东方财富热搜股票"""
    try:
        import akshare as ak
        df = ak.stock_hot_search_em()
        if df is None or df.empty:
            return []

        results = []
        for _, row in df.head(top_n).iterrows():
            results.append({
                "name": str(row.get("股票名称", "")).strip(),
                "code": str(row.get("股票代码", "")).strip(),
                "rank": len(results) + 1,
            })
        return results
    except Exception as e:
        st.warning(f"热搜数据获取失败: {e}")
        return []


# ── 热门板块 ─────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_hot_sectors(top_n: int = 10) -> list:
    """获取概念板块涨幅排行"""
    try:
        import akshare as ak
        df = ak.stock_board_concept_name_em()
        if df is None or df.empty:
            return []

        # 按涨跌幅排序
        df_sorted = df.sort_values("涨跌幅", ascending=False)
        results = []
        for _, row in df_sorted.head(top_n).iterrows():
            results.append({
                "name": str(row.get("板块名称", "")).strip(),
                "change_pct": float(row["涨跌幅"]),
            })
        return results
    except Exception as e:
        st.warning(f"板块数据获取失败: {e}")
        return []


# ── 交易日历 ─────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_calendar() -> dict:
    """获取今日投资日历"""
    try:
        import akshare as ak
        today = datetime.now().strftime("%Y-%m-%d")
        # 检查是否为交易日
        df = ak.tool_trade_date_hist_sina()
        trade_dates = set(df["trade_date"].astype(str).values)

        is_trade_day = today in trade_dates
        return {
            "date": today,
            "is_trade_day": is_trade_day,
            "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()],
            "events": []  # 重大事件可扩展
        }
    except Exception as e:
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "is_trade_day": True,
            "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()],
            "events": [],
        }


# ── 批量获取所有数据 ─────────────────────────────────────────
def fetch_all_data() -> dict:
    """一次性获取所有数据，统一缓存"""
    return {
        "indexes": fetch_index_quotes(),
        "news": fetch_news(),
        "hot_stocks": fetch_hot_stocks(),
        "hot_sectors": fetch_hot_sectors(),
        "calendar": fetch_calendar(),
        "fetch_time": datetime.now().strftime("%H:%M:%S"),
    }
