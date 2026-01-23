FINANCIAL_PROFILE = {
    "name": "financial",
    "display_name": "金融行业",
    "description": "银行、保险、资产管理、投资银行",

    "fundamental_rules": {
        "growth_thresholds": {"excellent": 12, "good": 7, "fair": 3},
        "profitability_thresholds": {"excellent": 20, "good": 15, "fair": 10},
        "debt_safe_threshold": 10.0,  # 金融股负债率标准不同
        "debt_warning_threshold": 15.0,
        "pe_warning_threshold": 15,  # 金融股PE通常较低
        "pb_warning_threshold": 2.5,  # 市净率警告线
    },

    "key_metrics": [
        "净资产收益率(ROE)",
        "净息差(NIM)",
        "不良贷款率(NPL)",
        "资本充足率(CAR)",
        "市净率(P/B)",
        "股息收益率",
    ],

    "valuation_emphasis": "price_to_book",  # 金融股重点看市净率
    "technical_weight": 0.5,  # 技术分析权重降低

    "risk_factors": [
        "利率风险",
        "信用风险",
        "监管风险",
        "流动性风险",
        "经济周期风险",
    ],

    "special_notes": [
        "金融股技术分析参考性较低",
        "重点关注基本面和估值",
        "银行股需关注资本充足率和不良率",
        "保险股需关注投资组合和赔付率",
    ]
}