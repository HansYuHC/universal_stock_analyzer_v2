import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 从main导入分析函数
from main import analyze_stock_for_streamlit
from utils.helpers import get_industry_display_name

# 导入新函数
try:
    from main import analyze_for_web
    HAS_NEW_FUNCTION = True
except ImportError:
    HAS_NEW_FUNCTION = False
    # 如果新函数不存在，导入旧函数
    from main import analyze_stock_for_streamlit

# 页面配置
st.set_page_config(
    page_title="股票分析系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 会话状态初始化
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'report_content' not in st.session_state:
    st.session_state.report_content = ""
if 'current_ticker' not in st.session_state:
    st.session_state.current_ticker = ""


def main():
    st.title("📈 股票分析系统 v2.0")
    st.markdown("---")

    # 侧边栏
    with st.sidebar:
        st.header("🔍 股票分析")

        ticker = st.text_input(
            "股票代码",
            value=st.session_state.current_ticker or "AAPL",
            placeholder="例如: AAPL, GOOGL, TSLA"
        ).upper()

        use_cache = st.checkbox("使用缓存数据", value=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 开始分析", type="primary", use_container_width=True):
                with st.spinner(f"正在分析 {ticker}..."):
                    # 使用新的专为Web优化的函数
                    try:
                        # 从main导入新函数
                        from main import analyze_for_web
                        result = analyze_for_web(ticker, use_cache)
                    except ImportError:
                        # 如果新函数不存在，使用旧函数
                        st.warning("⚠️ 使用旧版分析函数，部分数据可能不完整")
                        result = analyze_stock_for_streamlit(ticker, use_cache)

                    if result['success']:
                        # 验证数据完整性
                        analysis_result = result['analysis_result']

                        # 检查关键数据是否存在
                        if 'supplementary' not in analysis_result:
                            st.warning("⚠️ 补充数据缺失，正在修复...")
                            # 尝试修复
                            if 'stock_data_snapshot' in analysis_result:
                                analysis_result['supplementary'] = {
                                    'basic_info': {'name': ticker},
                                    'financials': analysis_result['stock_data_snapshot'],
                                    'price_data': {},
                                    'valuation': {},
                                    'analyst': {},
                                    'company_dynamics': {}
                                }
                            else:
                                # 创建基本结构
                                analysis_result['supplementary'] = {
                                    'basic_info': {'name': ticker},
                                    'financials': {},
                                    'price_data': {},
                                    'valuation': {},
                                    'analyst': {},
                                    'company_dynamics': {}
                                }

                        # 保存到session state
                        st.session_state.analysis_result = analysis_result
                        st.session_state.report_content = result['report_content']
                        st.session_state.current_ticker = ticker
                        st.session_state.data_quality = result.get('data_quality', 'unknown')
                        st.session_state.full_result = result  # 保存完整结果

                        st.success(f"✅ {ticker} 分析完成！")

                        # 显示数据质量
                        with st.expander("📊 数据质量报告", expanded=False):
                            basic_info = analysis_result.get('supplementary', {}).get('basic_info', {})
                            financials = analysis_result.get('supplementary', {}).get('financials', {})

                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("公司名称", basic_info.get('name', ticker))
                                market_cap = financials.get('market_cap')
                                if market_cap:
                                    st.metric("市值", f"${market_cap / 1e9:.2f}B")
                                else:
                                    st.metric("市值", "数据暂缺")

                            with col2:
                                st.metric("数据质量", result.get('data_quality', 'unknown'))
                                revenue_growth = financials.get('revenue_growth')
                                if revenue_growth is not None:
                                    st.metric("营收增长", f"{revenue_growth:.1f}%")
                                else:
                                    st.metric("营收增长", "数据暂缺")

                    else:
                        st.error(f"❌ 分析失败: {result.get('error', '未知错误')}")

        with col2:
            if st.button("🔄 清除缓存", use_container_width=True):
                st.session_state.analysis_result = None
                st.session_state.report_content = ""
                st.session_state.current_ticker = ""
                st.session_state.full_result = None
                st.rerun()

        st.markdown("---")
        st.header("📊 热门股票")

        popular_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "JPM", "XOM", "KO", "NVO"]
        cols = st.columns(3)
        for idx, stock in enumerate(popular_stocks):
            with cols[idx % 3]:
                if st.button(stock, use_container_width=True):
                    st.session_state.current_ticker = stock
                    st.rerun()

        st.markdown("---")
        st.header("ℹ️ 使用说明")
        st.info("""
        1. 输入股票代码，点击"开始分析"
        2. 首次分析可能需要10-20秒
        3. 后续分析使用缓存，只需2-3秒
        4. 完整报告可在"📋 完整报告"标签页查看
        5. 可下载TXT报告保存或分享
        """)

    # 主内容区
    if st.session_state.get('analysis_result'):
        display_analysis_results()
    else:
        display_welcome()


def display_welcome():
    """显示欢迎页面"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("支持股票", "美股全市场", "")
        st.metric("数据源", "Yahoo Finance", "实时")

    with col2:
        st.metric("分析维度", "5大行业", "可扩展")
        st.metric("技术指标", "30+", "全面")

    with col3:
        st.metric("报告格式", "TXT + Web", "双输出")
        st.metric("缓存系统", "智能缓存", "6小时")

    st.markdown("---")

    # 功能展示
    st.subheader("🎯 核心功能")

    features = [
        {"title": "📊 全面分析", "desc": "基本面+技术面+宏观数据"},
        {"title": "📈 实时图表", "desc": "交互式价格与技术指标图表"},
        {"title": "📋 专业报告", "desc": "可下载的详细TXT分析报告"},
        {"title": "💾 智能缓存", "desc": "自动缓存加速重复分析"},
        {"title": "🏭 行业适配", "desc": "5大行业专用分析模型"},
        {"title": "🎯 交易信号", "desc": "量化模型生成投资建议"},
    ]

    cols = st.columns(3)
    for idx, feature in enumerate(features):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"**{feature['title']}**")
                st.caption(feature['desc'])


def display_analysis_results():
    """显示分析结果 - 修复版"""
    # 从session_state获取数据
    analysis_data = st.session_state.get('analysis_result')
    full_result = st.session_state.get('full_result')

    if not analysis_data:
        st.warning("❌ 没有分析数据，请先分析股票")
        return

    # 验证数据
    if not isinstance(analysis_data, dict):
        st.error(f"❌ 分析数据格式错误: 期待字典但得到 {type(analysis_data)}")
        return

    # 获取ticker
    ticker = st.session_state.get('current_ticker', '未知')

    # 从supplementary获取数据
    supplementary = analysis_data.get('supplementary', {})
    basic_info = supplementary.get('basic_info', {})
    financials = supplementary.get('financials', {})
    price_data = supplementary.get('price_data', {})

    # 公司名称
    company_name = basic_info.get('name', ticker)

    st.header(f"{ticker} - {company_name}")

    # 关键指标
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        current_price = price_data.get('latest', {}).get('current', 0) or supplementary.get('current_price', 0)
        change_pct = price_data.get('latest', {}).get('change_pct', 0)
        st.metric(
            "当前价格",
            f"${current_price:.2f}",
            f"{change_pct:+.2f}%" if change_pct != 0 else "",
            delta_color="normal"
        )

    with col2:
        market_cap = financials.get('market_cap', 0)
        if market_cap > 0:
            st.metric("市值", f"${market_cap / 1e9:.2f}B")
        else:
            st.metric("市值", "数据暂缺")

    with col3:
        pe_ratio = supplementary.get('valuation', {}).get('trailing_pe', 0)
        st.metric("市盈率(PE)", f"{pe_ratio:.1f}" if pe_ratio > 0 else "N/A")

    with col4:
        signal = analysis_data.get('signal', {})
        recommendation = signal.get('recommendation', 'N/A')
        confidence = signal.get('confidence', 0)
        st.metric("投资建议", recommendation, f"信心: {confidence:.1f}/5.0")

    st.markdown("---")

    # 标签页 - 你需要确保这些函数也能正确处理新数据格式
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 价格走势",
        "📊 技术分析",
        "💰 基本面",
        "📋 完整报告",
        "📥 下载"
    ])

    with tab1:
        display_price_chart(price_data, ticker)

    with tab2:
        display_technical_analysis(analysis_data)

    with tab3:
        display_fundamental_analysis(analysis_data)

    with tab4:
        display_full_report()

    with tab5:
        display_download_section()


def display_price_chart(price_data, ticker):
    """显示价格图表"""
    if 'history' in price_data and not price_data['history'].empty:
        df = price_data['history']

        # 创建图表
        fig = go.Figure()

        # 价格线
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='收盘价',
            line=dict(color='#3B82F6', width=2)
        ))

        # 添加移动平均线
        if len(df) > 20:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Close'].rolling(20).mean(),
                mode='lines',
                name='20日均线',
                line=dict(color='#EF4444', width=1, dash='dash')
            ))

        fig.update_layout(
            title=f"{ticker} 价格走势",
            xaxis_title="日期",
            yaxis_title="价格 ($)",
            hovermode='x unified',
            height=500,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # 价格统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("52周高点", f"${df['Close'].max():.2f}")
        with col2:
            st.metric("52周低点", f"${df['Close'].min():.2f}")
        with col3:
            current = price_data.get('latest', {}).get('current', 0)
            vs_high = ((current / df['Close'].max()) - 1) * 100
            st.metric("距高点", f"{vs_high:.1f}%")
    else:
        st.warning("暂无价格数据")


def display_technical_analysis(analysis_data):
    """显示技术分析"""
    tech_indicators = analysis_data.get('technical_indicators', {})

    if tech_indicators:
        # 技术指标卡片
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            momentum = tech_indicators.get('momentum', {})
            rsi = momentum.get('rsi_14', 50)
            rsi_status = "🔴超买" if rsi > 70 else "🟢超卖" if rsi < 30 else "⚪正常"
            st.metric("RSI(14)", f"{rsi:.1f}", rsi_status)

        with col2:
            trend = tech_indicators.get('trend', {})
            macd_signal = trend.get('macd_signal', 'neutral')
            signal_text = "看涨" if macd_signal == 'bullish' else "看跌" if macd_signal == 'bearish' else "中性"
            st.metric("MACD信号", signal_text)

        with col3:
            signals = tech_indicators.get('signals', {})
            overall = signals.get('overall_signal', '中性')
            st.metric("综合信号", overall)

        with col4:
            technicals = analysis_data.get('technicals', {})
            tech_score = technicals.get('score', 0)
            tech_max = technicals.get('max_score', 6)
            st.metric("技术评分", f"{tech_score}/{tech_max}")

        # 更多技术指标...
        st.subheader("📊 技术指标详情")

        tech_details = {
            "趋势强度": trend.get('trend_strength', 'N/A'),
            "布林带位置": f"{trend.get('bb_position', 0) * 100:.1f}%",
            "随机指标K值": f"{momentum.get('stoch_k', 0):.1f}",
            "波动率(ATR%)": f"{tech_indicators.get('volatility', {}).get('atr_percent', 0):.1f}%",
        }

        cols = st.columns(4)
        for idx, (key, value) in enumerate(tech_details.items()):
            with cols[idx]:
                st.metric(key, value)
    else:
        st.info("技术指标数据正在计算中...")


def display_fundamental_analysis(analysis_data):
    """显示基本面分析"""
    fundamentals = analysis_data.get('fundamentals', {})
    financials = analysis_data['supplementary']['financials']

    # 基本面评分
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        fund_score = fundamentals.get('score', 0)
        fund_max = fundamentals.get('max_score', 8)
        st.metric("基本面评分", f"{fund_score}/{fund_max}", fundamentals.get('rating', 'N/A'))

    with col2:
        revenue_growth = financials.get('revenue_growth', 0)
        st.metric("营收增长", f"{revenue_growth:.1f}%")

    with col3:
        profit_margin = financials.get('profit_margin', 0)
        st.metric("净利润率", f"{profit_margin:.1f}%")

    with col4:
        roe = financials.get('return_on_equity', 0)
        st.metric("净资产收益率", f"{roe:.1f}%")

    # 财务健康度
    st.subheader("💪 财务健康度")

    health_cols = st.columns(4)
    with health_cols[0]:
        debt_ratio = financials.get('debt_to_equity', 0)
        st.metric("负债权益比", f"{debt_ratio:.2f}")

    with health_cols[1]:
        current_ratio = financials.get('current_ratio', 0)
        st.metric("流动比率", f"{current_ratio:.2f}")

    with health_cols[2]:
        fcf = financials.get('free_cashflow', 0)
        st.metric("自由现金流", f"${fcf / 1e6:.1f}M" if fcf else "N/A")

    with health_cols[3]:
        operating_margin = financials.get('operating_margin', 0)
        st.metric("营业利润率", f"{operating_margin:.1f}%")

    # 关键因素
    if 'key_reasons' in fundamentals:
        st.subheader("🔍 关键因素")
        for reason in fundamentals['key_reasons'][:4]:
            st.write(f"• {reason}")


def display_full_report():
    """显示完整报告"""
    st.subheader("📋 完整分析报告")

    # 显示报告内容
    st.text_area(
        "报告内容",
        st.session_state.report_content,
        height=600,
        label_visibility="collapsed"
    )


def display_download_section():
    """显示下载区域"""
    st.subheader("📥 下载选项")

    # TXT报告下载
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{st.session_state.current_ticker}_analysis_{timestamp}.txt"

    st.download_button(
        label="💾 下载TXT报告",
        data=st.session_state.report_content,
        file_name=filename,
        mime="text/plain",
        use_container_width=True
    )

    # 数据导出
    st.markdown("---")
    st.subheader("📊 数据导出")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("导出价格数据 (CSV)", use_container_width=True):
            # 这里可以添加价格数据导出功能
            st.info("价格数据导出功能开发中...")

    with col2:
        if st.button("导出分析结果 (JSON)", use_container_width=True):
            # 这里可以添加JSON导出功能
            st.info("JSON导出功能开发中...")


if __name__ == "__main__":
    main()