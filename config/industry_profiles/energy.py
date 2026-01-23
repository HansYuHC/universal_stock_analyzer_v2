ENERGY_PROFILE = {
    "name": "energy",
    "display_name": "能源行业",
    "description": "石油、天然气、可再生能源",

    "fundamental_rules": {
        "growth_thresholds": {"excellent": 15, "good": 8, "fair": 3},
        "profitability_thresholds": {"excellent": 25, "good": 15, "fair": 8},
        "debt_safe_threshold": 0.7,
        "debt_warning_threshold": 1.2,
        "pe_warning_threshold": 30,
    },

    "key_metrics": ["每股现金流", "储量替代率", "桶油成本", "股息收益率"],
    "risk_factors": ["油价波动", "地缘政治", "能源转型", "环境监管"],
}