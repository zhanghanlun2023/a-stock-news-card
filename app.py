"""
A股每日新闻卡片 - Streamlit 应用
每天早上9:00自动更新，全天候展示最新A股市场资讯
部署: Streamlit Cloud (连接GitHub自动部署)
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import sys
import os

# 添加utils到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.data_fetcher import fetch_all_data


# ═══════════════════════════════════════════════════════════
# 页面配置
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="A股每日新闻卡片",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════
# CSS 样式
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ── 全局 ── */
    .stApp {
        background: #f5f6fa;
    }
    [data-testid="stAppViewContainer"] {
        padding: 0;
    }
    .main-container {
        max-width: 1280px;
        margin: 0 auto;
        padding: 0 20px 40px;
    }

    /* ── Header ── */
    .header-bar {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 28px 40px;
        border-radius: 0 0 16px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
    }
    .header-title {
        color: #ffffff;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 2px;
    }
    .header-subtitle {
        color: #a0aec0;
        font-size: 13px;
        margin-top: 4px;
    }
    .header-date {
        color: #e2e8f0;
        font-size: 14px;
        text-align: right;
    }
    .header-status {
        color: #48bb78;
        font-size: 12px;
    }
    .header-status.off {
        color: #f56565;
    }

    /* ── 指数卡片 ── */
    .index-row {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
    }
    .index-card {
        flex: 1;
        background: #ffffff;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border-left: 4px solid #e2e8f0;
        transition: all 0.2s;
    }
    .index-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        transform: translateY(-1px);
    }
    .index-name {
        font-size: 13px;
        color: #718096;
        margin-bottom: 6px;
    }
    .index-price {
        font-size: 26px;
        font-weight: 700;
        color: #1a202c;
        font-family: 'SF Mono', 'Consolas', monospace;
    }
    .index-change {
        font-size: 14px;
        font-weight: 600;
        margin-top: 4px;
    }
    .index-change.up { color: #e53e3e; }
    .index-change.down { color: #38a169; }
    .index-change.neutral { color: #718096; }
    .index-volume {
        font-size: 12px;
        color: #a0aec0;
        margin-top: 8px;
    }

    /* ── 内容区 ── */
    .content-row {
        display: flex;
        gap: 20px;
    }
    .news-main {
        flex: 2.2;
    }
    .sidebar-panel {
        flex: 0.8;
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    /* ── 新闻区 ── */
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-icon {
        font-size: 18px;
    }
    .news-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .news-item {
        padding: 12px 0;
        border-bottom: 1px solid #f7fafc;
        display: flex;
        gap: 12px;
        align-items: flex-start;
    }
    .news-item:last-child {
        border-bottom: none;
        padding-bottom: 0;
    }
    .news-badge {
        flex-shrink: 0;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        white-space: nowrap;
        margin-top: 2px;
    }
    .badge-policy {
        background: #fefcbf;
        color: #975a16;
    }
    .badge-industry {
        background: #c6f6d5;
        color: #276749;
    }
    .badge-stock {
        background: #fed7d7;
        color: #9b2c2c;
    }
    .badge-intl {
        background: #bee3f8;
        color: #2a4365;
    }
    .news-title {
        font-size: 14px;
        font-weight: 600;
        color: #2d3748;
        line-height: 1.5;
        flex: 1;
    }
    .news-meta {
        font-size: 11px;
        color: #a0aec0;
        margin-top: 4px;
        display: flex;
        gap: 12px;
    }

    /* ── 关键词高亮 ── */
    .hl-red { background: #fed7d7; padding: 1px 4px; border-radius: 3px; font-weight: 600; }
    .hl-orange { background: #feebc8; padding: 1px 4px; border-radius: 3px; font-weight: 600; }
    .hl-blue { background: #bee3f8; padding: 1px 4px; border-radius: 3px; font-weight: 600; }
    .hl-green { background: #c6f6d5; padding: 1px 4px; border-radius: 3px; font-weight: 600; }

    /* ── 热搜 ── */
    .hot-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid #f7fafc;
    }
    .hot-item:last-child { border-bottom: none; }
    .hot-rank {
        width: 22px;
        height: 22px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 700;
        color: #fff;
        flex-shrink: 0;
    }
    .hot-rank.r1 { background: #e53e3e; }
    .hot-rank.r2 { background: #ed8936; }
    .hot-rank.r3 { background: #ecc94b; color: #744210; }
    .hot-rank.rn { background: #a0aec0; }
    .hot-name { font-size: 13px; font-weight: 600; color: #2d3748; }
    .hot-code { font-size: 11px; color: #a0aec0; }

    /* ── 板块 ── */
    .sector-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #f7fafc;
    }
    .sector-item:last-child { border-bottom: none; }
    .sector-name { font-size: 13px; color: #4a5568; }
    .sector-pct { font-size: 13px; font-weight: 700; }
    .sector-pct.up { color: #e53e3e; }
    .sector-pct.down { color: #38a169; }

    /* ── 日历 ── */
    .calendar-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 12px;
        padding: 16px 20px;
        color: #fff;
        text-align: center;
    }
    .cal-date {
        font-size: 28px;
        font-weight: 700;
    }
    .cal-weekday {
        font-size: 13px;
        opacity: 0.85;
        margin-top: 2px;
    }
    .cal-status {
        font-size: 12px;
        margin-top: 8px;
        padding: 4px 12px;
        border-radius: 10px;
        display: inline-block;
    }
    .cal-status.open {
        background: rgba(72, 187, 120, 0.3);
    }
    .cal-status.close {
        background: rgba(245, 101, 101, 0.3);
    }

    /* ── Footer ── */
    .refresh-bar {
        text-align: center;
        padding: 16px;
        color: #a0aec0;
        font-size: 12px;
    }

    /* ── 按钮 ── */
    .stButton > button {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: #fff;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(26, 26, 46, 0.3);
    }

    /* ── 空状态 ── */
    .empty-state {
        text-align: center;
        padding: 40px;
        color: #a0aec0;
    }
    .empty-state .icon { font-size: 48px; }
    .empty-state .msg { font-size: 14px; margin-top: 8px; }

    /* ── 响应式 ── */
    @media (max-width: 900px) {
        .content-row { flex-direction: column; }
        .index-row { flex-direction: column; }
        .header-bar { padding: 20px 24px; flex-direction: column; gap: 8px; text-align: center; }
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# 关键词高亮函数
# ═══════════════════════════════════════════════════════════
HIGHLIGHT_MAP = {
    "重磅": "hl-red", "突发": "hl-red", "紧急": "hl-red",
    "政策": "hl-orange", "央行": "hl-orange", "证监会": "hl-orange", "降准": "hl-orange", "降息": "hl-orange",
    "涨停": "hl-red", "跌停": "hl-green",
    "涨超": "hl-red", "跌超": "hl-green",
    "暴涨": "hl-red", "暴跌": "hl-green",
    "突破": "hl-blue", "创新高": "hl-red", "创新低": "hl-green",
    "半导体": "hl-blue", "AI": "hl-blue", "人工智能": "hl-blue", "芯片": "hl-blue",
    "算力": "hl-blue", "机器人": "hl-blue", "自动驾驶": "hl-blue",
    "新能源": "hl-green", "光伏": "hl-green", "锂电池": "hl-green",
    "分红": "hl-orange", "回购": "hl-orange",
}


def highlight_text(text: str) -> str:
    """对标题中的关键词进行高亮"""
    result = text
    for kw, cls in sorted(HIGHLIGHT_MAP.items(), key=lambda x: -len(x[0])):
        if kw in result:
            result = result.replace(kw, f'<span class="{cls}">{kw}</span>')
    return result


# ═══════════════════════════════════════════════════════════
# 渲染函数
# ═══════════════════════════════════════════════════════════

def render_header():
    """渲染页面顶部"""
    today = datetime.now()
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][today.weekday()]
    date_str = today.strftime("%Y年%m月%d日")

    st.markdown(f"""
    <div class="header-bar">
        <div>
            <div class="header-title">📰 A股每日新闻卡片</div>
            <div class="header-subtitle">全市场资讯一站式汇总 · 每日9:00自动更新</div>
        </div>
        <div>
            <div class="header-date">{date_str} {weekday}</div>
            <div class="header-status" id="status-indicator">● 数据已就绪</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_indexes(indexes: list):
    """渲染三大指数行情卡片"""
    cols = st.columns(3)
    for i, idx in enumerate(indexes):
        with cols[i]:
            pct = idx["change_pct"]
            if pct > 0:
                change_class = "up"
                sign = "+"
            elif pct < 0:
                change_class = "down"
                sign = ""
            else:
                change_class = "neutral"
                sign = ""

            st.markdown(f"""
            <div class="index-card">
                <div class="index-name">{idx['name']}</div>
                <div class="index-price">{idx['price']:,.2f}</div>
                <div class="index-change {change_class}">
                    {sign}{pct:+.2f}% &nbsp; {sign}{idx['change_amt']:+.2f}
                </div>
                <div class="index-volume">成交额 {idx.get('volume', 0):,.0f}亿</div>
            </div>
            """, unsafe_allow_html=True)


def render_news_section(news_list: list):
    """渲染新闻列表"""
    # 按分类分组
    categories = ["政策要闻", "行业动态", "个股异动", "国际市场"]
    badge_map = {
        "政策要闻": ("badge-policy", "📋"),
        "行业动态": ("badge-industry", "🏭"),
        "个股异动": ("badge-stock", "📈"),
        "国际市场": ("badge-intl", "🌍"),
    }

    for cat in categories:
        cat_news = [n for n in news_list if n["category"] == cat]
        if not cat_news:
            continue

        badge_cls, icon = badge_map.get(cat, ("badge-policy", "📋"))

        items_html = ""
        for n in cat_news:
            title = highlight_text(n["title"])
            items_html += f"""
            <div class="news-item">
                <span class="news-badge {badge_cls}">{icon} {cat}</span>
                <div>
                    <div class="news-title">{title}</div>
                    <div class="news-meta">
                        <span>📡 {n['source']}</span>
                        <span>🕐 {n['time'][:10] if n['time'] else '--'}</span>
                        {f'<span>⭐ 热度 {n.get("score", 0)}</span>' if n.get("score", 0) >= 5 else ''}
                    </div>
                </div>
            </div>"""

        st.markdown(f"""
        <div class="news-card">
            <div class="section-title">
                <span class="section-icon">{icon}</span> {cat}
                <span style="font-size:12px;color:#a0aec0;font-weight:400;margin-left:8px;">
                    {len(cat_news)}条
                </span>
            </div>
            {items_html}
        </div>
        """, unsafe_allow_html=True)


def render_hot_stocks(stocks: list):
    """渲染热搜股票"""
    if not stocks:
        return

    items_html = ""
    for s in stocks:
        rank = s["rank"]
        rank_cls = "r1" if rank == 1 else ("r2" if rank == 2 else ("r3" if rank == 3 else "rn"))
        items_html += f"""
        <div class="hot-item">
            <span class="hot-rank {rank_cls}">{rank}</span>
            <span class="hot-name">{s['name']}</span>
            <span class="hot-code">{s['code']}</span>
        </div>"""

    st.markdown(f"""
    <div class="news-card">
        <div class="section-title">
            <span class="section-icon">🔥</span> 热搜股票
        </div>
        {items_html}
    </div>
    """, unsafe_allow_html=True)


def render_hot_sectors(sectors: list):
    """渲染热门板块"""
    if not sectors:
        return

    items_html = ""
    for s in sectors:
        pct = s["change_pct"]
        pct_cls = "up" if pct > 0 else ("down" if pct < 0 else "")
        sign = "+" if pct > 0 else ""
        items_html += f"""
        <div class="sector-item">
            <span class="sector-name">{s['name']}</span>
            <span class="sector-pct {pct_cls}">{sign}{pct:.2f}%</span>
        </div>"""

    st.markdown(f"""
    <div class="news-card">
        <div class="section-title">
            <span class="section-icon">📊</span> 热门板块
        </div>
        {items_html}
    </div>
    """, unsafe_allow_html=True)


def render_calendar(cal: dict):
    """渲染交易日历"""
    today = datetime.now()
    date_str = today.strftime("%m/%d")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][today.weekday()]
    is_trade = cal.get("is_trade_day", True)

    status_text = "🟢 交易日" if is_trade else "🔴 休市"
    status_cls = "open" if is_trade else "close"

    st.markdown(f"""
    <div class="calendar-card">
        <div class="cal-date">{date_str}</div>
        <div class="cal-weekday">{weekday}</div>
        <div class="cal-status {status_cls}">{status_text}</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════════════════════
def main():
    render_header()

    # ── 操作栏 ──
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.caption("数据来源：东方财富 · AKShare · 实时更新")
    with col2:
        auto_refresh = st.checkbox("🔄 自动刷新", value=True, help="每10分钟自动刷新数据")
    with col3:
        if st.button("🔄 立即刷新", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── 自动刷新JS ──
    if auto_refresh:
        components.html("""
        <script>
        setTimeout(function() {
            window.location.reload();
        }, 600000);  // 10分钟
        </script>
        """, height=0)

    # ── 数据加载 ──
    with st.spinner("📡 正在抓取最新市场数据..."):
        data = fetch_all_data()

    indexes = data["indexes"]
    news = data["news"]
    hot_stocks = data["hot_stocks"]
    hot_sectors = data["hot_sectors"]
    calendar = data["calendar"]
    fetch_time = data["fetch_time"]

    # ── 指数行情 ──
    render_indexes(indexes)

    # ── 主内容区：新闻 + 侧边栏 ──
    col_main, col_side = st.columns([2.2, 0.8])

    with col_main:
        if news and news[0].get("category") != "系统提示":
            render_news_section(news)
        else:
            st.markdown("""
            <div class="news-card">
                <div class="empty-state">
                    <div class="icon">📡</div>
                    <div class="msg">数据加载中，请点击"立即刷新"或等待自动刷新...</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_side:
        render_calendar(calendar)
        render_hot_stocks(hot_stocks)
        render_hot_sectors(hot_sectors)

    # ── Footer ──
    st.markdown(f"""
    <div class="refresh-bar">
        📡 数据更新时间：{fetch_time} &nbsp;|&nbsp;
        自动刷新：{'开启 (每10分钟)' if auto_refresh else '关闭'} &nbsp;|&nbsp;
        Powered by AKShare · Streamlit Cloud
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
