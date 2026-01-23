# 市场配置参数
MARKET_CONFIG = {
    # 市场状态判断阈值
    'market_status': {
        'bull_market_threshold': 20,  # 牛市中涨幅阈值
        'bear_market_threshold': -20,  # 熊市中跌幅阈值
        'correction_threshold': -10,  # 调整阈值
        'volatility_high_threshold': 30,  # 高波动率阈值
        'volatility_low_threshold': 15,  # 低波动率阈值
    },

    # 宏观经济指标权重
    'macro_weight': {
        'interest_rate': 0.25,
        'inflation': 0.20,
        'gdp_growth': 0.20,
        'unemployment': 0.15,
        'consumer_sentiment': 0.10,
        'manufacturing_pmi': 0.10,
    },

    # 行业轮动指标
    'sector_rotation': {
        'early_cycle': ['technology', 'consumer_cyclical', 'financials'],
        'mid_cycle': ['industrials', 'materials', 'energy'],
        'late_cycle': ['healthcare', 'consumer_defensive', 'utilities'],
        'recession': ['utilities', 'consumer_staples', 'healthcare'],
    },

    # 风险偏好配置
    'risk_preference': {
        'conservative': {
            'max_single_stock_weight': 0.05,
            'max_sector_weight': 0.20,
            'min_cash_ratio': 0.20,
            'target_volatility': 0.10,
        },
        'moderate': {
            'max_single_stock_weight': 0.08,
            'max_sector_weight': 0.25,
            'min_cash_ratio': 0.10,
            'target_volatility': 0.15,
        },
        'aggressive': {
            'max_single_stock_weight': 0.12,
            'max_sector_weight': 0.35,
            'min_cash_ratio': 0.05,
            'target_volatility': 0.20,
        },
    },

    # 流动性要求
    'liquidity_requirements': {
        'min_daily_volume': 100000,  # 最低日成交量
        'min_market_cap': 500000000,  # 最低市值（5亿美元）
        'min_price': 5,  # 最低股价
        'max_bid_ask_spread': 0.02,  # 最大买卖价差比例
    },

    # 交易成本
    'trading_costs': {
        'commission_rate': 0.0005,  # 佣金率
        'slippage_rate': 0.001,  # 滑点率
        'tax_rate_short_term': 0.35,  # 短期税率
        'tax_rate_long_term': 0.15,  # 长期税率
    },

    # 时间配置
    'time_settings': {
        'data_freshness_hours': 24,  # 数据新鲜度（小时）
        'cache_expiry_hours': 1,  # 缓存过期时间
        'market_hours': {  # 市场交易时间
            'us': {'open': '09:30', 'close': '16:00', 'timezone': 'America/New_York'},
            'hk': {'open': '09:30', 'close': '16:00', 'timezone': 'Asia/Hong_Kong'},
            'sh': {'open': '09:30', 'close': '15:00', 'timezone': 'Asia/Shanghai'},
        },
    },

    # 技术分析参数
    'technical_analysis': {
        'default_period': '2y',  # 默认数据周期
        'default_interval': '1d',  # 默认数据间隔
        'rsi_period': 14,  # RSI周期
        'macd_fast': 12,  # MACD快线
        'macd_slow': 26,  # MACD慢线
        'macd_signal': 9,  # MACD信号线
        'bb_period': 20,  # 布林带周期
        'bb_std': 2,  # 布林带标准差
        'atr_period': 14,  # ATR周期
    },

    # 回测配置
    'backtest_settings': {
        'default_initial_capital': 10000,  # 默认初始资金
        'min_data_points': 100,  # 最小数据点数
        'default_strategy': 'dual_momentum',  # 默认策略
        'benchmark_ticker': 'SPY',  # 基准指数
        'risk_free_rate': 0.02,  # 无风险利率
    },
}