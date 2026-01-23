HEALTHCARE_PROFILE = {
    "name": "healthcare",
    "display_name": "医疗保健",
    "description": "制药、生物科技、医疗设备",

    "fundamental_rules": {
        "growth_thresholds": {"excellent": 20, "good": 12, "fair": 6},
        "profitability_thresholds": {"excellent": 30, "good": 20, "fair": 10},
        "debt_safe_threshold": 0.6,
        "debt_warning_threshold": 1.0,
        "pe_warning_threshold": 35,
    },

    "key_metrics": ["研发费用占比", "毛利率", "新药批准", "专利到期"],
    "risk_factors": ["研发失败", "监管审批", "专利悬崖", "价格管制"],
}