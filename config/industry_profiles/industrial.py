INDUSTRIAL_PROFILE = {
    "name": "industrial",
    "display_name": "工业制造",
    "description": "机械、航空、建筑、电气设备",

    "fundamental_rules": {
        "growth_thresholds": {"excellent": 15, "good": 8, "fair": 3},
        "profitability_thresholds": {"excellent": 20, "good": 12, "fair": 6},
        "debt_safe_threshold": 0.8,
        "debt_warning_threshold": 1.5,
        "pe_warning_threshold": 25,
    },

    "key_metrics": ["订单增长率", "产能利用率", "毛利率", "存货周转"],
    "risk_factors": ["经济周期", "原材料成本", "贸易政策", "汇率波动"],
}