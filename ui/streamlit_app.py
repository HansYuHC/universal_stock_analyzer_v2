import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 导入模糊搜索工具
from utils.fuzzy_search import get_stock_searcher, auto_correct_symbol, get_popular_stocks

# 页面配置
st.set_page_config(
    page_title="全能股票分析系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stock-button {
        background-color: #F3F4F6;
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 4px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    .stock-button:hover {
        background-color: #E5E7EB;
        border-color: #9CA3AF;
    }
    .search-result-item {
        padding: 10px;
        border-bottom: 1px solid #E5E7EB;
        cursor: pointer;
    }
    .search-result-item:hover {
        background-color: #F3F4F6;
    }
    .correction-badge {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-left: 8px;
    }
</style>
""", unsafe_allow_html=True)


class StockAnalysisApp:
    """Streamlit股票分析应用"""

    def __init__(self):
        self.ticker = None
        self.data = None
        self.analysis_result = None
        self.stock_searcher = get_stock_searcher()

        # 初始化session state
        if 'current_ticker' not in st.session_state:
            st.session_state.current_ticker = ""
        if 'analysis_result' not in st.session_state:
            st.session_state.analysis_result = None
        if 'report_content' not in st.session_state:
            st.session_state.report_content = ""
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""

    def run(self):
        """运行应用"""
        st.markdown('<h1 class="main-header">📈 全能股票分析系统 v2.0</h1>', unsafe_allow_html=True)

        # 侧边栏
        with st.sidebar:
            self._display_sidebar()

        # 主界面
        if st.session_state.analysis_result:
            self._display_analysis_results()
        else:
            self._display_welcome()

    def _display_sidebar(self):
        """显示侧边栏"""
        st.header("🔍 股票搜索与分析")

        # 搜索框
        search_query = st.text_input(
            "搜索股票代码或公司名称",
            value=st.session_state.search_query,
            placeholder="例如: AAPL, Apple, fiserv, 谷歌",
            key="search_input"
        )

        if search_query and search_query != st.session_state.search_query:
            st.session_state.search_query = search_query
            # 执行搜索
            results = self.stock_searcher.find_stock(search_query, max_results=10)
            st.session_state.search_results = results

        # 显示搜索结果
        if st.session_state.search_results:
            st.subheader("📋 搜索结果")
            for i, stock in enumerate(st.session_state.search_results[:5]):
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button(f"📈 {stock['symbol']}", key=f"select_{i}", use_container_width=True):
                        st.session_state.current_ticker = stock['symbol']
                        st.rerun()
                with col2:
                    st.caption(stock['name'])
                    if stock.get('is_correction'):
                        st.caption("🔍 自动修正")

        # 直接输入（带自动修正）
        st.subheader("或直接输入代码")

        ticker_input = st.text_input(
            "股票代码",
            value=st.session_state.current_ticker,
            placeholder="输入股票代码",
            key="ticker_input"
        ).upper()

        # 自动修正显示
        if ticker_input and ticker_input != st.session_state.current_ticker:
            corrected_symbol, corrected_name = auto_correct_symbol(ticker_input)

            if corrected_symbol != ticker_input:
                st.info(f"🔍 自动修正: **{ticker_input}** → **{corrected_symbol}**")
                if st.button(f"使用 {corrected_symbol}", type="secondary", use_container_width=True):
                    st.session_state.current_ticker = corrected_symbol
                    st.rerun()
            else:
                st.session_state.current_ticker = ticker_input

        # 分析选项
        use_cache = st.checkbox("使用缓存数据", value=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 开始分析", type="primary", use_container_width=True):
                self._analyze_stock(st.session_state.current_ticker, use_cache)

        with col2:
            if st.button("🔄 清除缓存", use_container_width=True):
                st.session_state.analysis_result = None
                st.session_state.report_content = ""
                st.session_state.current_ticker = ""
                st.session_state.search_results = []
                st.session_state.search_query = ""
                st.rerun()

        st.divider()

        # 热门股票
        self._display_popular_stocks()

        # 使用说明
        with st.expander("ℹ️ 使用说明"):
            st.info("""
            1. 在搜索框输入公司名或代码（支持模糊搜索）
            2. 点击"开始分析"按钮
            3. 首次分析可能需要10-20秒
            4. 后续分析使用缓存，只需2-3秒
            5. 完整报告可在"📋 完整报告"标签页查看
            6. 可下载TXT报告保存或分享
            """)

    def _display_popular_stocks(self):
        """显示热门股票"""
        st.header("🚀 热门股票")

        # 按类别显示热门股票
        categories = {
            "technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"],
            "financial": ["JPM", "BAC", "V", "MA", "FISV", "GS", "MS"],
            "healthcare": ["JNJ", "PFE", "MRK", "ABT", "UNH", "LLY", "AMGN"],
            "consumer": ["WMT", "PG", "KO", "PEP", "MCD", "SBUX", "NKE"],
            "energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
            "communication": ["CMCSA", "T", "VZ", "TMUS", "DIS"],
        }

        # 创建标签页 - 确保标签数量正确
        tab_names = ["全部", "科技", "金融", "医疗", "消费", "其他"]
        tabs = st.tabs(tab_names)

        # 全部标签页
        with tabs[0]:
            cols = st.columns(4)
            all_stocks = []
            for cat_stocks in categories.values():
                all_stocks.extend(cat_stocks[:3])  # 每个类别取前3个

            for idx, symbol in enumerate(all_stocks[:12]):
                with cols[idx % 4]:
                    if st.button(symbol, key=f"all_{symbol}", use_container_width=True):
                        st.session_state.current_ticker = symbol
                        st.rerun()

        # 科技标签页
        with tabs[1]:
            tech_stocks = categories.get("technology", [])
            cols = st.columns(3)
            for idx, symbol in enumerate(tech_stocks):
                with cols[idx % 3]:
                    if st.button(symbol, key=f"tech_{symbol}", use_container_width=True):
                        st.session_state.current_ticker = symbol
                        st.rerun()

        # 金融标签页
        with tabs[2]:
            finance_stocks = categories.get("financial", [])
            cols = st.columns(3)
            for idx, symbol in enumerate(finance_stocks):
                with cols[idx % 3]:
                    if st.button(symbol, key=f"fin_{symbol}", use_container_width=True):
                        st.session_state.current_ticker = symbol
                        st.rerun()

        # 医疗标签页
        with tabs[3]:
            healthcare_stocks = categories.get("healthcare", [])
            cols = st.columns(3)
            for idx, symbol in enumerate(healthcare_stocks):
                with cols[idx % 3]:
                    if st.button(symbol, key=f"health_{symbol}", use_container_width=True):
                        st.session_state.current_ticker = symbol
                        st.rerun()

        # 消费标签页
        with tabs[4]:
            consumer_stocks = categories.get("consumer", [])
            cols = st.columns(3)
            for idx, symbol in enumerate(consumer_stocks):
                with cols[idx % 3]:
                    if st.button(symbol, key=f"cons_{symbol}", use_container_width=True):
                        st.session_state.current_ticker = symbol
                        st.rerun()

        # 其他标签页（能源和通信）
        with tabs[5]:
            st.subheader("能源")
            energy_stocks = categories.get("energy", [])
            cols_energy = st.columns(3)
            for idx, symbol in enumerate(energy_stocks):
                with cols_energy[idx % 3]:
                    if st.button(symbol, key=f"energy_{symbol}", use_container_width=True):
                        st.session_state.current_ticker = symbol
                        st.rerun()

            st.subheader("通信")
            comm_stocks = categories.get("communication", [])
            cols_comm = st.columns(3)
            for idx, symbol in enumerate(comm_stocks):
                with cols_comm[idx % 3]:
                    if st.button(symbol, key=f"comm_{symbol}", use_container_width=True):
                        st.session_state.current_ticker = symbol
                        st.rerun()

    def _analyze_stock(self, ticker, use_cache):
        """分析股票"""
        if not ticker:
            st.warning("请输入股票代码")
            return

        with st.spinner(f"正在分析 {ticker}..."):
            try:
                # 首先进行模糊搜索修正
                corrected_symbol, corrected_name = auto_correct_symbol(ticker)

                # 显示修正信息
                if corrected_symbol != ticker:
                    st.info(f"✅ 自动修正: **{ticker}** → **{corrected_symbol}**")
                    ticker = corrected_symbol

                # 导入分析函数
                try:
                    from main import analyze_for_web
                    result = analyze_for_web(ticker, use_cache)
                except ImportError:
                    # 回退到旧函数
                    from main import analyze_stock_for_streamlit
                    result = analyze_stock_for_streamlit(ticker, use_cache)

                if result['success']:
                    # 验证数据完整性
                    analysis_result = result['analysis_result']

                    # 检查关键数据是否存在
                    if 'supplementary' not in analysis_result:
                        st.warning("⚠️ 补充数据缺失，正在修复...")
                        if 'stock_data_snapshot' in analysis_result:
                            analysis_result['supplementary'] = {
                                'basic_info': {'name': ticker},
                                'financials': analysis_result['stock_data_snapshot'],
                                'price_data': {},
                                'valuation': {},
                                'analyst': {},
                                'company_dynamics': {}
                            }

                    # 保存到session state
                    st.session_state.analysis_result = analysis_result
                    st.session_state.report_content = result['report_content']
                    st.session_state.current_ticker = ticker

                    st.success(f"✅ {ticker} 分析完成！")
                    st.balloons()

                else:
                    st.error(f"❌ 分析失败: {result.get('error', '未知错误')}")

                    # 提供相似股票建议
                    similar_stocks = self.stock_searcher.find_stock(ticker, max_results=5)
                    if similar_stocks:
                        st.subheader("💡 尝试这些相似股票:")
                        cols = st.columns(min(5, len(similar_stocks)))
                        for idx, stock in enumerate(similar_stocks):
                            with cols[idx % len(cols)]:
                                if st.button(f"{stock['symbol']}", use_container_width=True):
                                    st.session_state.current_ticker = stock['symbol']
                                    st.rerun()

            except Exception as e:
                st.error(f"❌ 分析过程出错: {str(e)}")
                import traceback
                with st.expander("查看错误详情"):
                    st.code(traceback.format_exc())

    def _display_welcome(self):
        """显示欢迎界面"""
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("支持股票", "500+ 只美股", "NYSE/NASDAQ")
            st.metric("数据源", "实时更新", "Yahoo Finance")

        with col2:
            st.metric("分析维度", "8大行业", "智能分类")
            st.metric("技术指标", "30+", "全面覆盖")

        with col3:
            st.metric("搜索功能", "模糊搜索", "拼写纠错")
            st.metric("缓存系统", "智能缓存", "6小时")

        st.divider()

        # 功能介绍
        st.subheader("✨ 核心功能")

        features = [
            {"icon": "🔍", "title": "智能搜索", "desc": "支持模糊匹配和拼写纠错"},
            {"icon": "📊", "title": "全面分析", "desc": "基本面+技术面+行业分析"},
            {"icon": "📈", "title": "实时图表", "desc": "交互式价格与技术指标图表"},
            {"icon": "📋", "title": "专业报告", "desc": "可下载的详细TXT分析报告"},
            {"icon": "💾", "title": "智能缓存", "desc": "自动缓存加速重复分析"},
            {"icon": "🎯", "title": "交易信号", "desc": "量化模型生成投资建议"},
        ]

        cols = st.columns(3)
        for idx, feature in enumerate(features):
            with cols[idx % 3]:
                st.markdown(f"### {feature['icon']} {feature['title']}")
                st.caption(feature['desc'])

        # 搜索示例
        st.divider()
        st.subheader("🔍 搜索示例")

        examples = [
            ("fiserv", "FISV (Fiserv Inc.)"),
            ("fiserw", "FISV (自动修正拼写错误)"),
            ("google", "GOOGL (Alphabet Inc.)"),
            ("comcast", "CMCSA (Comcast Corporation)"),
            ("apple", "AAPL (Apple Inc.)"),
            ("msft", "MSFT (Microsoft Corporation)"),
        ]

        for query, result in examples:
            st.write(f"• **{query}** → {result}")

    def _display_analysis_results(self):
        """显示分析结果"""
        result = st.session_state.analysis_result
        ticker = st.session_state.current_ticker

        # 从analysis_result获取数据
        supplementary = result.get('supplementary', {})
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
            signal = result.get('signal', {})
            recommendation = signal.get('recommendation', 'N/A')
            confidence = signal.get('confidence', 0)
            st.metric("投资建议", recommendation, f"信心: {confidence:.1f}/5.0")

        st.markdown("---")

        # 标签页
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 价格走势",
            "📊 技术分析",
            "💰 基本面",
            "📋 完整报告",
            "📥 下载"
        ])

        with tab1:
            self._display_price_chart(price_data, ticker)

        with tab2:
            self._display_technical_analysis(result)

        with tab3:
            self._display_fundamental_analysis(result)

        with tab4:
            self._display_full_report()

        with tab5:
            self._display_download_section()

    def _display_price_chart(self, price_data, ticker):
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
                vs_high = ((current / df['Close'].max()) - 1) * 100 if df['Close'].max() > 0 else 0
                st.metric("距高点", f"{vs_high:.1f}%")
        else:
            st.warning("暂无价格数据")

    def _display_technical_analysis(self, analysis_data):
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
        else:
            st.info("技术指标数据正在计算中...")

    def _display_fundamental_analysis(self, analysis_data):
        """显示基本面分析"""
        fundamentals = analysis_data.get('fundamentals', {})
        supplementary = analysis_data.get('supplementary', {})
        financials = supplementary.get('financials', {})

        # 基本面评分
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            fund_score = fundamentals.get('score', 0)
            fund_max = fundamentals.get('max_score', 8)
            st.metric("基本面评分", f"{fund_score}/{fund_max}", fundamentals.get('rating', 'N/A'))

        with col2:
            revenue_growth = financials.get('revenue_growth')
            if revenue_growth is not None:
                st.metric("营收增长", f"{revenue_growth:.1f}%")
            else:
                st.metric("营收增长", "数据暂缺")

        with col3:
            profit_margin = financials.get('profit_margin')
            if profit_margin is not None:
                st.metric("净利润率", f"{profit_margin:.1f}%")
            else:
                st.metric("净利润率", "数据暂缺")

        with col4:
            roe = financials.get('return_on_equity')
            if roe is not None:
                st.metric("净资产收益率", f"{roe:.1f}%")
            else:
                st.metric("净资产收益率", "数据暂缺")

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
            st.metric("自由现金流", f"${fcf / 1e6:.1f}M" if fcf and fcf != 0 else "N/A")

        with health_cols[3]:
            operating_margin = financials.get('operating_margin', 0)
            st.metric("营业利润率", f"{operating_margin:.1f}%")

    def _display_full_report(self):
        """显示完整报告"""
        st.subheader("📋 完整分析报告")

        # 显示报告内容
        st.text_area(
            "报告内容",
            st.session_state.report_content,
            height=600,
            label_visibility="collapsed"
        )

    def _display_download_section(self):
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

        st.markdown("---")
        st.info("📊 数据导出功能开发中...")


# 运行应用
if __name__ == "__main__":
    app = StockAnalysisApp()
    app.run()