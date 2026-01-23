# 技术分析配置
TECHNICAL_CONFIG = {
    # 趋势指标配置
    'trend_indicators': {
        'moving_averages': {
            'periods': [5, 10, 20, 50, 100, 200],
            'types': ['sma', 'ema', 'wma'],
            'cross_signals': {
                'golden_cross': [50, 200],  # 金叉：短线上穿长线
                'death_cross': [50, 200],  # 死叉：短线下穿长线
            }
        },
        'macd': {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'buy_signal': 'macd > signal',
            'sell_signal': 'macd < signal',
        },
        'adx': {
            'period': 14,
            'strong_trend_threshold': 25,
            'weak_trend_threshold': 20,
        },
        'ichimoku': {
            'conversion_period': 9,
            'base_period': 26,
            'leading_span_b_period': 52,
            'displacement': 26,
        },
    },

    # 动量指标配置
    'momentum_indicators': {
        'rsi': {
            'period': 14,
            'overbought': 70,
            'oversold': 30,
            'extreme_overbought': 80,
            'extreme_oversold': 20,
        },
        'stochastic': {
            'k_period': 14,
            'd_period': 3,
            'overbought': 80,
            'oversold': 20,
        },
        'cci': {
            'period': 20,
            'overbought': 100,
            'oversold': -100,
        },
        'williams_r': {
            'period': 14,
            'overbought': -20,
            'oversold': -80,
        },
        'mfi': {
            'period': 14,
            'overbought': 80,
            'oversold': 20,
        },
    },

    # 波动率指标配置
    'volatility_indicators': {
        'bollinger_bands': {
            'period': 20,
            'std_dev': 2,
            'band_width_threshold': {
                'high_volatility': 0.15,
                'low_volatility': 0.05,
            }
        },
        'atr': {
            'period': 14,
            'volatility_classification': {
                'high': 0.05,  # ATR/Price > 5%
                'medium': 0.02,  # ATR/Price > 2%
                'low': 0.01,  # ATR/Price > 1%
            }
        },
        'standard_deviation': {
            'period': 20,
            'annualization_factor': 252,  # 年化因子
        },
    },

    # 成交量指标配置
    'volume_indicators': {
        'obv': {
            'trend_confirmation_period': 20,
        },
        'vpt': {  # 量价趋势
            'period': 14,
        },
        'volume_ratio': {
            'high_volume_threshold': 1.5,  # 当前成交量/平均成交量
        },
        'vwap': {
            'deviation_threshold': 0.02,  # 价格偏离VWAP的阈值
        },
    },

    # 支撑阻力配置
    'support_resistance': {
        'lookback_period': 100,  # 回看周期
        'pivot_points': {
            'daily': True,
            'weekly': True,
            'monthly': True,
        },
        'fibonacci_levels': [0.236, 0.382, 0.5, 0.618, 0.786],
        'price_clustering_tolerance': 0.02,  # 价格聚类容忍度
    },

    # 形态识别配置
    'pattern_recognition': {
        'double_top_bottom': {
            'min_time_between_peaks': 20,  # 双顶/双底最小时间间隔
            'price_tolerance': 0.03,  # 价格容忍度
        },
        'head_shoulders': {
            'min_head_height': 0.08,  # 头部最小高度
            'neckline_break_threshold': 0.02,
        },
        'triangle_patterns': {
            'min_touch_points': 4,  # 最小接触点
            'breakout_confirmation': 0.02,  # 突破确认阈值
        },
        'flag_pennant': {
            'min_flag_length': 10,  # 旗形最小长度
            'pole_height_ratio': 0.3,  # 旗杆高度比例
        },
    },

    # 综合信号生成配置
    'signal_generation': {
        'weight_factors': {
            'trend': 0.30,
            'momentum': 0.25,
            'volatility': 0.15,
            'volume': 0.15,
            'pattern': 0.15,
        },
        'confidence_levels': {
            'very_high': 0.8,  # 80%以上置信度
            'high': 0.7,  # 70-80%
            'medium': 0.6,  # 60-70%
            'low': 0.5,  # 50-60%
            'very_low': 0.4,  # 40-50%
        },
        'position_sizing': {
            'max_position_size': 0.1,  # 最大仓位（占总资金）
            'default_position_size': 0.05,  # 默认仓位
            'stop_loss_pct': 0.08,  # 止损比例
            'take_profit_pct': 0.20,  # 止盈比例
        },
    },

    # 时间框架配置
    'timeframes': {
        'intraday': ['5m', '15m', '30m', '60m'],
        'daily': ['1d'],
        'weekly': ['1w'],
        'monthly': ['1mo'],
        'default': '1d',
    },
}