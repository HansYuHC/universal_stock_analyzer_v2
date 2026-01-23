"""
消费品行业配置（必需消费品）
包括：饮料、食品、日用品、零售等
"""

CONSUMER_STAPLES_PROFILE = {
    'display_name': '消费品(必需)',

    'fundamental_rules': {
        'growth_thresholds': {
            'excellent': 10,  # 必需品增长较慢
            'good': 5,
            'fair': 2,
        },
        'profitability_thresholds': {
            'excellent': 25,  # 品牌消费品通常有较高利润率
            'good': 15,
            'fair': 8,
        },
        'debt_safe_threshold': 1.5,  # 消费品通常负债较低
        'debt_warning_threshold': 2.5,
        'pe_warning_threshold': 35,  # PE通常合理
    },

    'technical_preferences': {
        'prefer_indicators': ['RSI', 'Volume', 'Moving_Averages'],
        'volatility_expectation': '低波动',  # 必需品波动较低
        'trend_persistence': '中',  # 趋势持续性中等
    },

    'valuation_metrics': {
        'primary': 'P/E',  # 主要看PE
        'secondary': ['P/B', 'P/S', 'Dividend_Yield'],
        'typical_range': {
            'P/E': (15, 25),
            'P/B': (3, 8),
            'P/S': (2, 5),
            'Dividend_Yield': (2, 4),
        }
    },

    'risk_factors': [
        '原材料成本波动',
        '消费者偏好变化',
        '监管政策影响',
        '汇率风险（跨国公司）',
        '市场竞争加剧',
        '供应链风险',
    ],

    'strength_factors': [
        '稳定现金流',
        '品牌护城河',
        '必需消费需求稳定',
        '定价能力',
        '分销网络优势',
    ],

    'investment_themes': [
        '品牌价值投资',
        '股息收益策略',
        '防御性配置',
        '全球扩张潜力',
        '产品创新驱动',
    ],

    'key_metrics_to_watch': [
        '毛利率变化',
        '市场份额',
        '同店销售额',
        '库存周转率',
        '自由现金流',
        '股息支付率',
        '品牌价值排名',
    ],

    'sector_specific_notes': '''
    必需消费品行业特点：
    1. 需求相对稳定，受经济周期影响较小
    2. 品牌和渠道是关键竞争壁垒
    3. 通常有稳定股息和良好现金流
    4. 关注原材料成本控制和定价能力
    5. 国际业务扩张是重要增长动力

    重点关注：
    - 品牌护城河深度
    - 分销网络效率
    - 新产品开发能力
    - 成本控制能力
    - 股息政策和股东回报
    '''
}