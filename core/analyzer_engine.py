import importlib
import pandas as pd


class UniversalAnalyzer:
    """通用分析引擎 - 支持5大行业"""

    def __init__(self, industry="software"):
        self.industry = industry
        self.profile = self._load_industry_profile()

    def _load_industry_profile(self):
        """加载行业配置 - 修复版"""
        try:
            module_name = f"config.industry_profiles.{self.industry}"
            print(f"🔍 尝试加载行业配置: {module_name}")

            module = importlib.import_module(module_name)
            profile = getattr(module, f"{self.industry.upper()}_PROFILE", None)

            if profile is None:
                raise AttributeError(f"模块 {module_name} 中没有找到 {self.industry.upper()}_PROFILE")

            print(f"✅ 成功加载 {self.industry} 行业配置")
            return profile

        except ImportError as e:
            print(f"⚠️  无法导入 {self.industry} 行业配置: {e}")
        except AttributeError as e:
            print(f"⚠️  配置结构错误: {e}")

        # 回退到软件行业
        try:
            from config.industry_profiles.software import SOFTWARE_PROFILE
            print(f"⚠️  使用默认软件行业配置")
            return SOFTWARE_PROFILE
        except:
            print(f"❌ 无法加载默认配置")
            # 返回一个基本的配置字典
            return {
                'display_name': self.industry,
                'fundamental_rules': {},
                'risk_factors': [],
                'key_metrics_to_watch': [],
                'investment_themes': []
            }

    def analyze(self, data):
        """执行完整分析"""
        fundamentals = self._analyze_fundamentals(data)
        technicals = self._analyze_technicals(data)
        signal = self._generate_signal(fundamentals, technicals, data)
        risks = self._identify_risks(data)

        return {
            'fundamentals': fundamentals,
            'technicals': technicals,
            'signal': signal,
            'risks': risks,
            'industry': self.industry,
            'profile': self.profile.get('display_name', self.industry),
        }

    def _analyze_fundamentals(self, data):
        """基本面分析（按行业规则）"""
        score = 0
        reasons = []

        # 获取行业特定阈值
        profile = self.profile.get('fundamental_rules', {})
        growth_thresholds = profile.get('growth_thresholds', {'excellent': 15, 'good': 8, 'fair': 3})
        margin_thresholds = profile.get('profitability_thresholds', {'excellent': 20, 'good': 12, 'fair': 5})

        # 1. 增长性分析
        revenue_growth = data.get('financials', {}).get('revenue_growth', 0)
        if revenue_growth >= growth_thresholds['excellent']:
            score += 2
            reasons.append(f"营收增长强劲: {revenue_growth:.1f}%")
        elif revenue_growth >= growth_thresholds['good']:
            score += 1
            reasons.append(f"营收稳定增长: {revenue_growth:.1f}%")
        elif revenue_growth >= growth_thresholds['fair']:
            reasons.append(f"营收增长一般: {revenue_growth:.1f}%")
        else:
            reasons.append(f"营收增长疲软: {revenue_growth:.1f}%")

        # 2. 盈利能力
        op_margin = data.get('financials', {}).get('operating_margin', 0)
        if op_margin >= margin_thresholds['excellent']:
            score += 2
            reasons.append(f"运营利润率优秀: {op_margin:.1f}%")
        elif op_margin >= margin_thresholds['good']:
            score += 1
            reasons.append(f"运营利润率良好: {op_margin:.1f}%")
        elif op_margin >= margin_thresholds['fair']:
            reasons.append(f"运营利润率一般: {op_margin:.1f}%")
        else:
            reasons.append(f"运营利润率偏低: {op_margin:.1f}%")

        # 3. 财务健康度（行业特定）
        debt_ratio = data.get('financials', {}).get('debt_to_equity', 10)
        debt_safe = profile.get('debt_safe_threshold', 1.0)

        if debt_ratio < debt_safe * 0.5:
            score += 2
            reasons.append(f"负债率很低: {debt_ratio:.2f}")
        elif debt_ratio < debt_safe:
            score += 1
            reasons.append(f"负债率适中: {debt_ratio:.2f}")
        else:
            reasons.append(f"负债率较高: {debt_ratio:.2f}")

        # 4. 现金流
        fcf = data.get('financials', {}).get('free_cashflow', 0)
        if fcf > 0:
            score += 1
            reasons.append("自由现金流为正")

        # 5. 估值合理性
        pe = data.get('valuation', {}).get('trailing_pe', 0)
        pe_warning = profile.get('pe_warning_threshold', 40)

        if 0 < pe < 25:
            score += 1
            reasons.append(f"PE估值合理: {pe:.1f}")
        elif pe >= pe_warning:
            reasons.append(f"PE估值偏高: {pe:.1f}")

        # 评级
        max_score = 8
        if score >= 6:
            rating = "优秀"
        elif score >= 4:
            rating = "良好"
        elif score >= 2:
            rating = "中等"
        else:
            rating = "疲弱"

        return {
            'score': score,
            'max_score': max_score,
            'rating': rating,
            'key_reasons': reasons,
            'detailed_metrics': {
                'revenue_growth': revenue_growth,
                'operating_margin': op_margin,
                'debt_to_equity': debt_ratio,
                'free_cashflow': fcf,
                'pe_ratio': pe,
            }
        }

    def _analyze_technicals(self, data):
        """技术面分析 - 修复版"""
        price_data = data.get('price_data', {})

        # 修复：检查正确的字段
        has_data = price_data.get('has_sufficient_data', False)
        if not has_data:
            # 尝试从其他字段判断是否有数据
            history = price_data.get('history', None)
            if isinstance(history, pd.DataFrame) and len(history) >= 10:
                has_data = True
            else:
                return {
                    'score': 0,
                    'max_score': 6,
                    'rating': '数据不足',
                    'key_reasons': ['无法获取足够的价格数据'],
                    'data_status': 'insufficient',
                }

        score = 0
        reasons = []

        # 1. 相对52周高点位置
        stats = price_data.get('stats', {})
        current_vs_high = stats.get('current_vs_high', 0)

        if current_vs_high < -30:
            score += 2
            reasons.append(f"深度回调(低于52周高点{abs(current_vs_high):.1f}%)")
        elif current_vs_high < -15:
            score += 1
            reasons.append(f"中度回调(低于52周高点{abs(current_vs_high):.1f}%)")
        elif current_vs_high > -5:
            reasons.append(f"接近52周高点(仅低{abs(current_vs_high):.1f}%)")

        # 2. RSI分析
        technicals = price_data.get('technicals', {})
        rsi = technicals.get('rsi', 50)

        if rsi < 30:
            score += 2
            reasons.append(f"RSI超卖({rsi:.1f})")
        elif rsi < 40:
            score += 1
            reasons.append(f"RSI偏弱({rsi:.1f})")
        elif rsi > 70:
            reasons.append(f"RSI超买({rsi:.1f})")
            score -= 1

        # 3. 移动平均线分析
        ma20 = technicals.get('ma20', 0)
        ma50 = technicals.get('ma50', 0)
        current_price = price_data.get('latest', {}).get('current', 0)

        if current_price > 0:
            if current_price > ma20 and ma20 > ma50:
                score += 1
                reasons.append("价格在均线之上，呈多头排列")
            elif current_price < ma20 and ma20 < ma50:
                reasons.append("价格在均线之下，呈空头排列")
                score -= 1

        # 4. 成交量分析
        latest = price_data.get('latest', {})
        avg_volume = stats.get('avg_volume', 0) or stats.get('mean_volume', 0)
        volume = latest.get('volume', 0)

        if volume > 0 and avg_volume > 0:
            volume_ratio = volume / avg_volume
            if volume_ratio > 1.5:
                reasons.append(f"成交量放大({volume_ratio:.1f}x)")
                score += 0.5
            elif volume_ratio < 0.7:
                reasons.append(f"成交量萎缩({volume_ratio:.1f}x)")

        # 5. 短期价格变化
        change_pct = latest.get('change_pct', 0)
        if change_pct > 3:
            reasons.append(f"短期强势上涨: +{change_pct:.1f}%")
            score += 0.5
        elif change_pct < -3:
            reasons.append(f"短期弱势下跌: {change_pct:.1f}%")

        # 6. 使用高级技术指标（如果可用）
        advanced_tech = data.get('technical_indicators', {})
        if advanced_tech:
            momentum = advanced_tech.get('momentum', {})
            if momentum.get('oversold', False):
                score += 1
                reasons.append("技术指标显示超卖")
            if momentum.get('overbought', False):
                score -= 1
                reasons.append("技术指标显示超买")

        # 限制分数范围
        score = max(min(score, 6), 0)

        # 评级
        max_score = 6
        if score >= 4.5:
            rating = "超卖/机会"
        elif score >= 3:
            rating = "中性偏强"
        elif score >= 1.5:
            rating = "中性"
        elif score > 0:
            rating = "中性偏弱"
        else:
            rating = "谨慎"

        return {
            'score': score,
            'max_score': max_score,
            'rating': rating,
            'key_reasons': reasons,
            'data_status': 'sufficient',
            'indicators_used': {
                'rsi': rsi,
                'current_vs_high': current_vs_high,
                'volume_ratio': volume / avg_volume if volume > 0 and avg_volume > 0 else 0,
            }
        }

    def _generate_signal(self, fundamentals, technicals, data):
        """生成交易信号 - 修复版"""
        fund_score = fundamentals['score']
        tech_score = technicals['score']

        fund_ratio = fund_score / fundamentals['max_score'] if fundamentals['max_score'] > 0 else 0
        tech_ratio = tech_score / technicals['max_score'] if technicals['max_score'] > 0 else 0

        # 处理技术面数据不足的情况
        if technicals.get('data_status') == 'insufficient':
            # 如果技术面数据不足，主要依赖基本面
            if fund_ratio >= 0.7:
                recommendation = "基本面良好（技术数据不足）"
                confidence = 3.0
            elif fund_ratio >= 0.4:
                recommendation = "观望（技术数据不足）"
                confidence = 2.5
            else:
                recommendation = "谨慎（技术数据不足）"
                confidence = 2.0

            reasoning = f"基本面评分{fund_score}/{fundamentals['max_score']}，技术面数据不足"

            return {
                'recommendation': recommendation,
                'confidence': confidence,
                'reasoning': reasoning,
            }

        # 正常信号生成逻辑
        # 行业特定信号生成
        if self.industry == "energy":
            # 能源股更注重现金和技术面
            if fund_ratio >= 0.6 and tech_ratio >= 0.7:
                recommendation = "考虑配置"
                confidence = 4.0
            elif tech_ratio >= 0.8:
                recommendation = "技术面机会"
                confidence = 3.5
            else:
                recommendation = "观望"
                confidence = 2.5

        elif self.industry == "financial":
            # 金融股注重基本面和估值
            if fund_ratio >= 0.7 and data.get('valuation', {}).get('price_to_book', 10) < 2:
                recommendation = "估值吸引"
                confidence = 4.0
            else:
                recommendation = "谨慎"
                confidence = 3.0

        else:  # 默认策略
            if fund_ratio >= 0.6 and tech_ratio >= 0.6:
                recommendation = "考虑买入"
                confidence = 4.0
            elif fund_ratio >= 0.4 and tech_ratio >= 0.7:
                recommendation = "技术面机会"
                confidence = 3.5
            elif tech_ratio >= 0.8:
                recommendation = "超卖反弹机会"
                confidence = 3.0
            elif tech_ratio >= 0.6 and fund_ratio >= 0.3:
                recommendation = "观望偏多"
                confidence = 2.8
            elif fund_ratio >= 0.5 and tech_ratio >= 0.3:
                recommendation = "基本面支撑"
                confidence = 2.8
            else:
                recommendation = "观望"
                confidence = 2.5

        reasoning = f"基本面评分{fund_score}/{fundamentals['max_score']}({fund_ratio:.1%})，技术面评分{tech_score}/{technicals['max_score']}({tech_ratio:.1%})"

        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'reasoning': reasoning,
        }

    def _identify_risks(self, data):
        """识别风险（行业特定）"""
        risks = []
        profile = self.profile

        # 行业通用风险
        generic_risks = profile.get('risk_factors', [])
        risks.extend(generic_risks[:2])  # 只取前2个

        # 财务风险
        debt_ratio = data.get('financials', {}).get('debt_to_equity', 0)
        debt_warning = profile.get('fundamental_rules', {}).get('debt_warning_threshold', 2.0)

        if debt_ratio > debt_warning:
            risks.append(f"高负债风险 (负债率: {debt_ratio:.2f})")

        # 估值风险
        pe = data.get('valuation', {}).get('trailing_pe', 0)
        pe_danger = profile.get('fundamental_rules', {}).get('pe_warning_threshold', 40)

        if pe > pe_danger:
            risks.append(f"高估值风险 (PE: {pe:.1f})")

        # 增长风险
        revenue_growth = data.get('financials', {}).get('revenue_growth', 0)
        if revenue_growth < 0:
            risks.append("营收负增长")

        # 技术面数据风险
        technicals = data.get('technical_indicators', {})
        if technicals and technicals.get('data_quality') == 'enhanced':
            risks.append("技术分析基于部分模拟数据")

        return risks[:3]  # 最多返回3个风险