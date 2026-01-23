"""
改进版报告生成器
"""
from datetime import datetime
import os
from typing import Dict, Any
import json


class ReportGenerator:
    """改进版报告生成器 - 提供更全面的分析"""

    def __init__(self, ticker: str, industry: str, analysis_result: Dict[str, Any]):
        self.ticker = ticker
        self.industry = industry
        self.result = analysis_result
        self.timestamp = datetime.now()

        # 数据验证和修复
        self._validate_and_fix_data()

    def _validate_and_fix_data(self):
        """验证和修复数据完整性"""
        # 确保有supplementary数据
        if 'supplementary' not in self.result:
            self.result['supplementary'] = {}

        supplementary = self.result['supplementary']

        # 确保所有必要的子字典都存在
        required_keys = ['basic_info', 'financials', 'valuation', 'price_data', 'analyst', 'company_dynamics']
        for key in required_keys:
            if key not in supplementary:
                supplementary[key] = {}

        # 如果basic_info中没有name，使用ticker
        if not supplementary['basic_info'].get('name'):
            supplementary['basic_info']['name'] = self.ticker

        # 确保profile是字典
        if 'profile' not in self.result or not isinstance(self.result['profile'], dict):
            self.result['profile'] = {
                'display_name': self.industry,
                'risk_factors': ['通用行业风险'],
                'key_metrics_to_watch': [],
                'investment_themes': []
            }

    def generate(self) -> str:
        """生成完整报告"""
        report = []

        # 1. 报告头部
        report.append("=" * 70)
        report.append(f"📊 股票分析报告 - {self.ticker}")
        report.append("=" * 70)
        report.append("")

        # 2. 公司基本信息
        report.append("一、公司概况")
        report.append("-" * 40)
        report.extend(self._generate_company_info())
        report.append("")

        # 3. 核心结论
        report.append("二、核心投资结论")
        report.append("-" * 40)
        report.extend(self._generate_core_conclusion())
        report.append("")

        # 4. 基本面深度分析
        report.append("三、基本面深度分析")
        report.append("-" * 40)
        report.extend(self._generate_fundamental_analysis())
        report.append("")

        # 5. 技术面分析
        report.append("四、技术面分析")
        report.append("-" * 40)
        report.extend(self._generate_technical_analysis())
        report.append("")

        # 6. 估值分析
        report.append("五、估值与成长性")
        report.append("-" * 40)
        report.extend(self._generate_valuation_analysis())
        report.append("")

        # 7. 风险提示
        report.append("六、风险提示")
        report.append("-" * 40)
        report.extend(self._generate_risk_analysis())
        report.append("")

        # 8. 操作策略建议
        report.append("七、操作策略建议")
        report.append("-" * 40)
        report.extend(self._generate_strategy_recommendation())
        report.append("")

        # 9. 行业洞察与展望
        report.append("八、行业洞察与展望")
        report.append("-" * 40)
        report.extend(self._generate_industry_insights())
        report.append("")

        # 10. 投资逻辑总结
        report.append("九、投资逻辑总结")
        report.append("-" * 40)
        report.extend(self._generate_investment_logic())
        report.append("")

        # 11. 数据来源与免责声明
        report.append("=" * 70)
        report.append(self._generate_disclaimer())
        report.append("=" * 70)

        return "\n".join(report)

    def _generate_company_info(self):
        """生成公司基本信息 - 修复版"""
        info = []

        # 从supplementary获取数据
        supplementary = self.result.get('supplementary', {})

        # 基本信息
        basic_info = supplementary.get('basic_info', {})
        financials = supplementary.get('financials', {})
        valuation = supplementary.get('valuation', {})
        price_data = supplementary.get('price_data', {})

        # 公司名称 - 多重回退
        company_name = (
                basic_info.get('name') or
                self.result.get('basic_info', {}).get('name') or
                self.ticker
        )

        # 当前价格 - 多重回退
        current_price = (
                supplementary.get('current_price') or
                price_data.get('latest', {}).get('current') or
                self.result.get('current_price') or
                0
        )

        info.append(f"🏢 公司全称: {company_name}")
        info.append(f"📊 股票代码: {self.ticker}")
        info.append(f"🏭 所属板块: {basic_info.get('sector', '未分类')}")
        info.append(f"🔍 细分行业: {basic_info.get('industry', '未分类')}")

        # 市值计算
        market_cap = financials.get('market_cap', 0)
        if market_cap > 0:
            info.append(f"💰 当前市值: ${market_cap / 1e9:.2f}B")
        else:
            info.append(f"💰 当前市值: 数据暂缺")

        info.append(f"💵 当前股价: ${current_price:.2f}")

        # 关键财务指标 - 添加数据检查
        info.append("\n📈 关键财务指标:")

        metrics = [
            ('年营收增长', financials.get('revenue_growth'), '%.1f%%'),
            ('营业利润率', financials.get('operating_margin'), '%.1f%%'),
            ('净利润率', financials.get('profit_margin'), '%.1f%%'),
            ('ROE(净资产收益率)', financials.get('return_on_equity'), '%.1f%%'),
            ('负债权益比', financials.get('debt_to_equity'), '%.2f'),
        ]

        for label, value, fmt in metrics:
            if value is not None:
                info.append(f"   • {label}: {fmt % value}")
            else:
                info.append(f"   • {label}: 数据暂缺")

        # 最新动态 - 修复字符串格式化问题
        info.append("\n📰 最新动态:")

        dynamics = supplementary.get('company_dynamics', {})
        if dynamics:
            # 财报日期
            last_earnings = dynamics.get('last_earnings_date', '暂无数据')
            info.append(f"   • 最新财报: {last_earnings}")

            # 重大事件
            major_events = dynamics.get('major_events', [])
            if major_events and major_events[0] != '暂无监测到重大事件':
                info.append(f"   • 近期大事: {', '.join(major_events[:2])}")

            # 分析师关注度
            coverage = dynamics.get('analyst_coverage', '中等')
            count = dynamics.get('analyst_count', 0)
            info.append(f"   • 分析师关注度: {coverage}({count}位)")
        else:
            info.append(f"   • 最新财报: 数据获取中")
            info.append(f"   • 近期大事: 数据获取中")
            info.append(f"   • 分析师关注度: 中等")

        # 相关链接
        info.append("\n🔗 相关链接:")
        info.append(f"   • 公司官网: https://www.{self.ticker.lower()}.com")
        info.append(f"   • Yahoo财经: https://finance.yahoo.com/quote/{self.ticker}")
        info.append(f"   • SeekingAlpha: https://seekingalpha.com/symbol/{self.ticker}")
        info.append(f"   • Google新闻: https://www.google.com/search?q={self.ticker}+stock+news&tbm=nws")

        return info

    def _generate_core_conclusion(self):
        """生成核心结论"""
        signal = self.result.get('signal', {})
        fundamentals = self.result.get('fundamentals', {})
        technicals = self.result.get('technicals', {})

        info = []

        # 投资建议
        recommendation = signal.get('recommendation', '观望')
        confidence = signal.get('confidence', 2.5)

        # 根据建议类型添加表情符号
        emoji_map = {
            '买入': '🟢',
            '增持': '🟢',
            '持有': '🟡',
            '观望': '🟡',
            '减持': '🔴',
            '卖出': '🔴',
            '谨慎': '🟡'
        }

        emoji = emoji_map.get(recommendation, '⚪')

        info.append(f"{emoji} 投资建议: {recommendation}")
        info.append(f"📊 信心指数: {confidence:.1f}/5.0")
        info.append("")

        # 综合评分
        fund_score = fundamentals.get('score', 0)
        fund_max = fundamentals.get('max_score', 8)
        tech_score = technicals.get('score', 0)
        tech_max = technicals.get('max_score', 6)

        info.append(f"📈 综合评分: {fund_score + tech_score}/{fund_max + tech_max}")
        info.append(f"   • 基本面: {fund_score}/{fund_max} ({fund_score / fund_max * 100:.1f}%)")
        info.append(f"   • 技术面: {tech_score}/{tech_max} ({tech_score / tech_max * 100:.1f}%)")
        info.append("")

        # 核心逻辑
        reasoning = signal.get('reasoning', '')
        info.append("🎯 核心逻辑:")
        info.append(f"   {reasoning}")
        info.append("")

        # 关键看点
        info.append("🔍 关键看点:")
        fund_reasons = fundamentals.get('key_reasons', [])
        tech_reasons = technicals.get('key_reasons', [])

        # 取最重要的3个原因
        all_reasons = fund_reasons[:2] + tech_reasons[:1]
        for i, reason in enumerate(all_reasons[:3], 1):
            info.append(f"   {i}. {reason}")

        return info

    def _generate_fundamental_analysis(self):
        """生成基本面深度分析"""
        fundamentals = self.result.get('fundamentals', {})
        detailed = fundamentals.get('detailed_metrics', {})

        info = []

        # 评分和评级
        rating = fundamentals.get('rating', '中等')
        score = fundamentals.get('score', 0)
        max_score = fundamentals.get('max_score', 8)

        info.append(f"📊 综合评级: {rating} ({score}/{max_score})")
        info.append("")

        # 增长性分析
        revenue_growth = detailed.get('revenue_growth', 0)
        info.append("📈 增长性分析:")
        if revenue_growth > 15:
            info.append(f"   ✅ 营收增长强劲({revenue_growth:.1f}%)，公司处于快速成长期")
        elif revenue_growth > 5:
            info.append(f"   ⚪ 营收稳步增长({revenue_growth:.1f}%)，显示稳定发展态势")
        elif revenue_growth > 0:
            info.append(f"   ⚠️  营收增长缓慢({revenue_growth:.1f}%)，需关注增长动力")
        else:
            info.append(f"   ❌ 营收负增长({revenue_growth:.1f}%)，经营面临挑战")

        # 盈利能力分析
        op_margin = detailed.get('operating_margin', 0)
        info.append("💰 盈利能力分析:")
        if op_margin > 20:
            info.append(f"   ✅ 运营利润率优秀({op_margin:.1f}%)，盈利能力强")
        elif op_margin > 10:
            info.append(f"   ⚪ 运营利润率良好({op_margin:.1f}%)，盈利水平合理")
        else:
            info.append(f"   ⚠️  运营利润率偏低({op_margin:.1f}%)，需关注成本控制")

        # 财务健康度
        debt_ratio = detailed.get('debt_to_equity', 0)
        info.append("💪 财务健康度:")
        if debt_ratio < 0.5:
            info.append(f"   ✅ 负债率很低({debt_ratio:.2f})，财务结构稳健")
        elif debt_ratio < 1.0:
            info.append(f"   ⚪ 负债率适中({debt_ratio:.2f})，杠杆运用合理")
        elif debt_ratio < 2.0:
            info.append(f"   ⚠️  负债率较高({debt_ratio:.2f})，需关注偿债能力")
        else:
            info.append(f"   ❌ 负债率过高({debt_ratio:.2f})，存在财务风险")

        # 现金流分析
        fcf = detailed.get('free_cashflow', 0)
        info.append("💵 现金流分析:")
        if fcf > 0:
            info.append(f"   ✅ 自由现金流为正(约${fcf / 1e6:.1f}M)，财务状况健康")
        else:
            info.append(f"   ⚠️  自由现金流为负，需关注资金状况")

        return info

    def _generate_technical_analysis(self):
        """生成技术面分析"""
        technicals = self.result.get('technicals', {})
        indicators = self.result.get('technical_indicators', {})

        info = []

        # 技术面评分
        rating = technicals.get('rating', '中性')
        score = technicals.get('score', 0)
        max_score = technicals.get('max_score', 6)

        info.append(f"📊 技术面评级: {rating} ({score}/{max_score})")

        # 如果没有足够数据
        if score == 0 and rating == '数据不足':
            info.append("⚠️  技术分析提示: 历史价格数据不足，分析结果仅供参考")
            info.append("   建议结合其他分析方法综合判断")
            return info

        # 趋势分析
        trend = indicators.get('trend', {})
        info.append("\n📈 趋势分析:")
        trend_strength = trend.get('trend_strength', '横盘')
        macd_signal = trend.get('macd_signal', 'neutral')

        if '上升' in trend_strength:
            info.append(f"   ↗️  当前处于{trend_strength}趋势")
        elif '下降' in trend_strength:
            info.append(f"   ↘️  当前处于{trend_strength}趋势")
        else:
            info.append(f"   ➡️  当前处于{trend_strength}状态")

        if macd_signal == 'bullish':
            info.append(f"   📈 MACD显示看涨信号")
        elif macd_signal == 'bearish':
            info.append(f"   📉 MACD显示看跌信号")

        # 动量分析
        momentum = indicators.get('momentum', {})
        info.append("\n⚡ 动量分析:")
        rsi = momentum.get('rsi_14', 50)
        stoch_k = momentum.get('stoch_k', 50)

        if rsi < 30:
            info.append(f"   🟢 RSI({rsi:.1f})处于超卖区域，可能出现反弹")
        elif rsi > 70:
            info.append(f"   🔴 RSI({rsi:.1f})处于超买区域，注意回调风险")
        else:
            info.append(f"   ⚪ RSI({rsi:.1f})处于中性区域")

        if momentum.get('oversold', False):
            info.append("   🟢 多个指标显示超卖，技术性反弹机会")
        if momentum.get('overbought', False):
            info.append("   🔴 多个指标显示超买，注意调整风险")

        # 关键价位
        price_data = self.result.get('price_data', {})
        stats = price_data.get('stats', {})
        info.append("\n🎯 关键价位:")
        info.append(f"   • 当前 vs 52周高点: {stats.get('current_vs_high', 0):.1f}%")
        info.append(f"   • 支撑位(近期低点): ${stats.get('min', 0):.2f}")
        info.append(f"   • 阻力位(近期高点): ${stats.get('max', 0):.2f}")

        return info

    def _generate_valuation_analysis(self):
        """生成估值分析"""
        valuation = self.result.get('valuation', {})

        info = []

        # PE分析
        trailing_pe = valuation.get('trailing_pe', 0)
        forward_pe = valuation.get('forward_pe', 0)

        info.append("💰 市盈率(P/E)分析:")
        if 0 < trailing_pe < 20:
            info.append(f"   ✅ 当前PE({trailing_pe:.1f})处于合理偏低区间")
        elif 20 <= trailing_pe < 30:
            info.append(f"   ⚪ 当前PE({trailing_pe:.1f})处于行业平均水平")
        elif trailing_pe >= 30:
            info.append(f"   ⚠️  当前PE({trailing_pe:.1f})偏高，需关注估值风险")

        if forward_pe > 0 and forward_pe < trailing_pe:
            info.append(f"   📈 预期PE({forward_pe:.1f})低于当前，显示盈利增长预期")

        # PB分析
        price_to_book = valuation.get('price_to_book', 0)
        info.append("\n📚 市净率(P/B)分析:")
        if 0 < price_to_book < 3:
            info.append(f"   ✅ P/B({price_to_book:.2f})合理，估值相对安全")
        elif price_to_book >= 3:
            info.append(f"   ⚠️  P/B({price_to_book:.2f})偏高，需关注资产质量")

        # PEG分析
        peg_ratio = valuation.get('peg_ratio', 0)
        info.append("\n📊 成长估值(PEG)分析:")
        if 0 < peg_ratio < 1:
            info.append(f"   ✅ PEG({peg_ratio:.2f})<1，成长性估值具吸引力")
        elif 1 <= peg_ratio < 2:
            info.append(f"   ⚪ PEG({peg_ratio:.2f})合理，成长与估值匹配")
        elif peg_ratio >= 2:
            info.append(f"   ⚠️  PEG({peg_ratio:.2f})偏高，成长性需验证")

        # 综合估值判断
        info.append("\n🎯 综合估值判断:")
        attractiveness = valuation.get('attractiveness', '合理')
        if attractiveness == '有吸引力':
            info.append("   ✅ 当前估值具吸引力，安全边际较高")
        elif attractiveness == '合理':
            info.append("   ⚪ 估值处于合理区间，反映基本面状况")
        else:
            info.append("   ⚠️  估值偏高，需谨慎评估增长预期")

        return info

    def _generate_risk_analysis(self):
        """生成风险分析 - 修复版"""
        risks = self.result.get('risks', [])
        industry_profile = self.result.get('profile', {})

        # 检查industry_profile是否是字典
        if isinstance(industry_profile, str):
            # 如果是字符串，尝试从supplementary获取
            supplementary = self.result.get('supplementary', {})
            if supplementary:
                industry_profile = supplementary.get('profile', {})

        info = []

        # 行业固有风险
        if isinstance(industry_profile, dict):
            industry_risks = industry_profile.get('risk_factors', [])
            if industry_risks:
                info.append("⚠️  行业固有风险:")
                for i, risk in enumerate(industry_risks[:3], 1):
                    info.append(f"   {i}. {risk}")
        else:
            # 备用风险提示
            info.append("⚠️  行业风险:")
            info.append("   1. 行业政策变化风险")
            info.append("   2. 市场竞争加剧风险")
            info.append("   3. 技术迭代风险")

        # 公司特定风险
        if risks:
            info.append("\n⚠️  公司特定风险:")
            for i, risk in enumerate(risks[:3], 1):
                info.append(f"   {i}. {risk}")

        # 市场风险
        info.append("\n⚠️  市场风险:")
        info.append("   1. 宏观经济波动风险")
        info.append("   2. 利率政策变化影响")
        info.append("   3. 市场流动性风险")
        info.append("   4. 地缘政治风险")

        # 风险评级
        risk_count = len(risks) + 3  # 固定市场风险数量
        info.append(f"\n📊 风险评估: {'低' if risk_count < 3 else '中' if risk_count < 5 else '高'}风险")

        return info

    def _generate_strategy_recommendation(self):
        """生成操作策略建议"""
        signal = self.result.get('signal', {})
        recommendation = signal.get('recommendation', '观望')
        confidence = signal.get('confidence', 2.5)

        info = []

        # 根据不同建议生成策略
        if recommendation in ['买入', '增持']:
            info.append("🟢 积极配置策略:")
            info.append("   1. 可分批建仓，避免一次性投入")
            info.append("   2. 建议仓位: 5-10% (根据风险承受能力调整)")
            info.append("   3. 止损位设置: -8% 至 -10%")
            info.append("   4. 目标收益: 15-25%")
            info.append("   5. 持有期建议: 6-12个月")

        elif recommendation in ['观望', '持有']:
            info.append("🟡 观望/持有策略:")
            info.append("   1. 已持仓者可继续持有")
            info.append("   2. 未持仓者建议等待更好时机")
            info.append("   3. 关注关键价位突破情况")
            info.append("   4. 密切跟踪公司财报和行业动态")
            info.append("   5. 可少量试探性建仓")

        else:  # 减持/卖出/谨慎
            info.append("🔴 谨慎/减持策略:")
            info.append("   1. 考虑减仓或暂时离场")
            info.append("   2. 已持仓者设置严格止损")
            info.append("   3. 未持仓者建议规避")
            info.append("   4. 关注风险因素的演变")
            info.append("   5. 等待更明确信号再行动")

        # 操作要点
        info.append("\n🎯 操作要点:")
        info.append("   • 建议结合技术面和基本面综合决策")
        info.append("   • 控制单只股票仓位不超过15%")
        info.append("   • 定期复盘和调整策略")
        info.append("   • 保持投资纪律，避免情绪化操作")

        return info

    def _generate_industry_insights(self):
        """生成行业洞察"""
        industry = self.industry
        profile = self.result.get('profile', {})

        info = []

        info.append("🌍 行业现状与趋势:")

        # 根据不同行业生成洞察
        industry_insights = {
            'software': "软件行业正处于数字化转型浪潮中，云计算、AI、SaaS是主要增长驱动力。",
            'energy': "能源行业面临绿色转型挑战，传统能源与新能源共存，价格波动性较大。",
            'financial': "金融行业受利率政策和监管环境影响显著，数字化和合规是主要趋势。",
            'healthcare': "医疗健康行业受益于人口老龄化和技术创新，但受政策监管较强。",
            'industrial': "工业制造受益于全球供应链重构和自动化升级，但周期性强。",
            'consumer_staples': "必需品消费需求稳定，但面临原材料成本上升和消费升级挑战。",
        }

        insight = industry_insights.get(industry, "该行业具有其特定的发展规律和周期性特征。")
        info.append(f"   {insight}")

        # 行业关键驱动因素
        key_factors = profile.get('key_metrics_to_watch', [])
        if key_factors:
            info.append("\n📊 行业关键驱动因素:")
            for i, factor in enumerate(key_factors[:5], 1):
                info.append(f"   {i}. {factor}")

        # 投资主题
        themes = profile.get('investment_themes', [])
        if themes:
            info.append("\n💡 当前投资主题:")
            for i, theme in enumerate(themes[:3], 1):
                info.append(f"   {i}. {theme}")

        return info

    def _generate_investment_logic(self):
        """生成投资逻辑总结"""
        signal = self.result.get('signal', {})
        fundamentals = self.result.get('fundamentals', {})
        technicals = self.result.get('technicals', {})

        info = []

        info.append("🎯 投资逻辑框架:")
        info.append("")

        # 基本面逻辑
        fund_rating = fundamentals.get('rating', '中等')
        fund_reasons = fundamentals.get('key_reasons', [])

        info.append(f"📈 基本面逻辑({fund_rating}):")
        for reason in fund_reasons[:2]:
            info.append(f"   • {reason}")

        # 技术面逻辑
        tech_rating = technicals.get('rating', '中性')
        tech_reasons = technicals.get('key_reasons', [])

        info.append(f"\n📊 技术面逻辑({tech_rating}):")
        if tech_reasons:
            for reason in tech_reasons[:2]:
                info.append(f"   • {reason}")
        else:
            info.append("   • 技术面信号不明确")

        # 综合判断
        info.append("\n🤔 综合判断:")
        reasoning = signal.get('reasoning', '')
        info.append(f"   {reasoning}")

        # 后续关注点
        info.append("\n👀 后续关注点:")
        info.append("   1. 公司下一季度财报表现")
        info.append("   2. 行业政策变化")
        info.append("   3. 技术面关键价位突破")
        info.append("   4. 宏观经济数据")

        return info

    def _generate_disclaimer(self):
        """生成免责声明"""
        return f"""
重要声明:
1. 本报告基于公开信息和量化模型自动生成，仅供参考，不构成投资建议。
2. 数据来源: Yahoo Finance API，数据截止至 {self.timestamp.strftime('%Y-%m-%d')}。
3. 投资有风险，入市需谨慎。请结合自身风险承受能力和投资目标独立决策。
4. 过往表现不预示未来收益，市场可能波动剧烈。
5. 建议投资者进行充分研究，必要时咨询专业投资顾问。
生成时间: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""

    def save_to_file(self):
        """保存报告到文件"""
        report_content = self.generate()

        # 创建outputs目录
        os.makedirs('outputs', exist_ok=True)

        # 生成文件名
        timestamp = self.timestamp.strftime('%Y%m%d_%H%M%S')
        filename = f"outputs/{self.ticker}_{self.industry}_{timestamp}.txt"

        # 保存文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return filename