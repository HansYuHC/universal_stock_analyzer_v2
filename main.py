#!/usr/bin/env python3
"""
股票分析系统 v2.0 - 带缓存优化版
"""
import sys
import os
from datetime import datetime

sys.path.extend([
    os.path.join(os.path.dirname(__file__), 'core'),
    os.path.join(os.path.dirname(__file__), 'config'),
    os.path.join(os.path.dirname(__file__), 'utils')
])

from core.data_fetcher import UniversalDataFetcher
from core.analyzer_engine import UniversalAnalyzer
from core.technical_analyzer import AdvancedTechnicalAnalyzer
from core.report_generator import ReportGenerator
from utils.helpers import detect_industry, get_industry_display_name, get_cache_stats
from utils.technical_helper import TechnicalDataEnhancer  # 新增导入


def main():
    """主程序"""
    print("=" * 70)
    print("📈 股票分析系统 v2.0 (缓存优化版)")
    print("=" * 70)

    # 显示缓存状态
    show_cache_status()

    # 获取股票代码
    ticker = input("\n请输入股票代码 (例如: AAPL, XOM, JPM): ").strip().upper()
    if not ticker:
        print("❌ 必须输入股票代码")
        return

    # 缓存选项
    use_cache = True
    cache_option = input(f"\n使用缓存分析 {ticker}? (y/n, 默认y): ").strip().lower()
    if cache_option == 'n':
        use_cache = False
        print("⚠️  禁用缓存，将从网络下载数据")

    print(f"\n🚀 开始分析 {ticker} ...")

    try:
        start_time = datetime.now()

        # 1. 获取实时数据（带缓存）
        print("📥 获取数据...")
        fetcher = UniversalDataFetcher(ticker, use_cache=use_cache)
        stock_data = fetcher.fetch_comprehensive_data()

        # 显示缓存状态
        if fetcher.cache_hit:
            print("   💾 使用缓存数据 (速度优化)")
        else:
            print("   🌐 从网络下载数据")

        # 2. 确保有足够的技术分析数据
        print("📊 准备技术分析数据...")
        stock_data = TechnicalDataEnhancer.ensure_sufficient_data(stock_data, min_days=60)

        # 3. 自动检测行业
        industry = detect_industry(ticker, stock_data)
        industry_display = get_industry_display_name(industry)
        print(f"📋 行业分类: {industry_display}")

        # 4. 基本面分析
        print("💰 基本面分析...")
        analyzer = UniversalAnalyzer(industry)
        analysis_result = analyzer.analyze(stock_data)

        # 5. 高级技术分析
        print("📈 技术分析...")
        price_data = stock_data.get('price_data', {})
        tech_analyzer = AdvancedTechnicalAnalyzer(price_data)
        tech_indicators = tech_analyzer.calculate_all_indicators()

        # 添加数据来源标记
        if stock_data.get('data_quality', 'full') != 'full':
            tech_indicators['data_quality'] = 'enhanced'
            tech_indicators['data_source'] = '模拟+实际数据'
        else:
            tech_indicators['data_quality'] = 'full'
            tech_indicators['data_source'] = '实际数据'

        analysis_result['technical_indicators'] = tech_indicators

        # 6. 在分析结果中添加必要数据（提供给报告生成器）
        print("📋 准备分析数据...")
        analysis_result['ticker'] = ticker
        analysis_result['industry'] = industry
        analysis_result['basic_info'] = stock_data.get('basic_info', {})
        analysis_result['financials'] = stock_data.get('financials', {})
        analysis_result['valuation'] = stock_data.get('valuation', {})
        analysis_result['price_data'] = stock_data.get('price_data', {})
        analysis_result['current_price'] = stock_data['price_data']['latest']['current']
        analysis_result['profile'] = analyzer.profile  # 行业配置

        # 添加分析师数据
        analysis_result['analyst'] = stock_data.get('analyst', {})

        # 添加数据质量标记
        analysis_result['data_quality'] = stock_data.get('data_quality', 'full')

        # 7. 生成报告
        print("📄 生成报告...")
        reporter = ReportGenerator(ticker, industry, analysis_result)
        report_content = reporter.generate()
        report_file = reporter.save_to_file()

        # 8. 显示摘要（添加耗时信息）
        total_time = (datetime.now() - start_time).total_seconds()
        display_summary_with_timing(ticker, stock_data, analysis_result, report_file,
                                    industry_display, total_time, fetcher.cache_hit)

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()


def show_cache_status():
    """显示缓存状态"""
    cache_stats = get_cache_stats()
    print(f"\n💾 缓存状态:")
    print(f"   缓存文件: {cache_stats['total_files']} 个")
    print(f"   缓存大小: {cache_stats['total_size_mb']:.2f} MB")

    if cache_stats['stocks']:
        print(f"   已缓存股票: {', '.join(cache_stats['stocks'][:5])}")
        if len(cache_stats['stocks']) > 5:
            print(f"   等共 {len(cache_stats['stocks'])} 只股票")

    print(f"   缓存位置: data/cache/")
    print(f"   缓存有效期: 6小时")


def display_summary_with_timing(ticker, stock_data, analysis_result, report_file,
                                industry_display, total_time, cache_hit):
    """显示带耗时信息的摘要"""
    print("\n" + "=" * 70)
    print(f"📊 {ticker} 分析完成 - {industry_display}")
    print("=" * 70)

    # 性能信息
    print(f"\n⏱️  性能信息:")
    print(f"   总耗时: {total_time:.2f} 秒")
    print(f"   数据源: {'缓存' if cache_hit else '网络下载'}")

    # 实时价格
    price_data = stock_data.get('price_data', {})
    latest = price_data.get('latest', {})

    print(f"\n📈 价格信息:")
    print(f"   当前: ${latest.get('current', 0):.2f}")
    print(f"   涨跌: {latest.get('change_pct', 0):+.2f}%")

    # 显示公司名称
    basic_info = stock_data.get('basic_info', {})
    company_name = basic_info.get('name', ticker)
    print(f"   公司: {company_name}")

    print(f"   市值: ${stock_data.get('financials', {}).get('market_cap', 0) / 1e9:.2f}B")

    # 核心评分
    fund = analysis_result.get('fundamentals', {})
    tech = analysis_result.get('technicals', {})

    print(f"\n📊 核心评分:")
    print(f"   基本面: {fund.get('rating', 'N/A')} ({fund.get('score', 0)}/{fund.get('max_score', 8)})")
    print(f"   技术面: {tech.get('rating', 'N/A')} ({tech.get('score', 0)}/{tech.get('max_score', 6)})")

    # 技术指标
    tech_indicators = analysis_result.get('technical_indicators', {})
    if tech_indicators:
        momentum = tech_indicators.get('momentum', {})
        rsi = momentum.get('rsi_14', 50)
        print(f"\n📉 技术指标:")
        print(f"   RSI(14): {rsi:.1f} {'🔴超买' if rsi > 70 else '🟢超卖' if rsi < 30 else '⚪正常'}")

        trend = tech_indicators.get('trend', {})
        macd_signal = trend.get('macd_signal', 'neutral')
        print(f"   MACD信号: {macd_signal}")

        # 显示数据质量
        data_source = tech_indicators.get('data_source', '实际数据')
        print(f"   数据源: {data_source}")

    # 交易信号
    signal = analysis_result.get('signal', {})
    print(f"\n🎯 交易信号: {signal.get('recommendation', 'N/A')}")
    print(f"   信心指数: {signal.get('confidence', 0):.1f}/5.0")

    # 显示分析师目标价
    analyst = analysis_result.get('analyst', {})
    target_price = analyst.get('target_price', 0)
    upside = analyst.get('upside_potential', 0)
    current_price = latest.get('current', 0)

    if target_price > 0 and current_price > 0:
        print(f"\n🎯 分析师观点:")
        print(f"   目标价: ${target_price:.2f}")
        print(f"   上涨空间: {upside:+.1f}%")
        print(f"   建议: {analyst.get('recommendation', 'N/A')}")

    # 缓存建议
    print(f"\n💾 缓存建议:")
    if cache_hit:
        print("   ✅ 缓存有效，下次分析将更快")
    else:
        print("   📥 数据已缓存，下次分析将使用缓存")

    print(f"\n📁 完整报告: {report_file}")
    print("=" * 70)

    # 缓存管理选项
    cache_management(ticker)


def cache_management(ticker):
    """缓存管理选项"""
    print(f"\n🗂️  缓存管理:")
    print(f"   1. 清除 {ticker} 的缓存")
    print(f"   2. 查看所有缓存")
    print(f"   3. 继续分析其他股票")

    choice = input("\n选择操作 (1-3, 默认3): ").strip()

    if choice == '1':
        from core.data_fetcher import UniversalDataFetcher
        fetcher = UniversalDataFetcher(ticker, use_cache=False)
        fetcher.clear_cache()
    elif choice == '2':
        show_cache_status()

    # 是否继续分析
    continue_analysis = input("\n继续分析其他股票? (y/n): ").strip().lower()
    if continue_analysis == 'y':
        main()
    else:
        print("\n👋 感谢使用！")


def quick_examples():
    """快速示例"""
    print("\n🚀 快速示例 (已有缓存):")
    examples = [
        ("AAPL", "苹果公司"),
        ("MSFT", "微软公司"),
        ("GOOGL", "谷歌公司"),
        ("XOM", "埃克森美孚"),
        ("JPM", "摩根大通"),
        ("KO", "可口可乐"),
        ("PG", "宝洁公司"),
        ("JNJ", "强生公司"),
        ("WMT", "沃尔玛"),
        ("V", "Visa公司"),
    ]

    for i, (symbol, name) in enumerate(examples, 1):
        print(f"   {i}. {symbol}: {name}")

    choice = input("\n快速分析 (输入编号或直接回车): ")
    if choice and choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(examples):
            # 这里可以设置直接调用分析逻辑
            print(f"\n分析 {examples[index][0]} ...")
            # 实际应该跳转到分析逻辑


# 在main.py中添加
def analyze_stock_for_streamlit(ticker, use_cache=True):
    """为Streamlit准备的分析函数 - 修复版"""
    try:
        print(f"🔍 Streamlit开始分析: {ticker}")

        # 获取数据
        fetcher = UniversalDataFetcher(ticker, use_cache=use_cache)
        stock_data = fetcher.fetch_comprehensive_data()

        print(f"✅ 数据获取成功，数据质量: {stock_data.get('data_quality', 'unknown')}")

        # 确保有足够的技术分析数据
        stock_data = TechnicalDataEnhancer.ensure_sufficient_data(stock_data, min_days=60)

        # 自动检测行业
        industry = detect_industry(ticker, stock_data)
        industry_display = get_industry_display_name(industry)
        print(f"📋 行业: {industry_display}")

        # 基本面分析
        analyzer = UniversalAnalyzer(industry)
        analysis_result = analyzer.analyze(stock_data)

        # 调试：检查profile类型
        print(f"🔍 analyzer.profile类型: {type(analyzer.profile)}")
        if isinstance(analyzer.profile, dict):
            print(f"✅ profile是字典，包含键: {list(analyzer.profile.keys())[:5]}")
        else:
            print(f"⚠️  profile不是字典，而是: {analyzer.profile}")

        # 高级技术分析
        price_data = stock_data.get('price_data', {})
        tech_analyzer = AdvancedTechnicalAnalyzer(price_data)
        tech_indicators = tech_analyzer.calculate_all_indicators()
        analysis_result['technical_indicators'] = tech_indicators

        # 确保analysis_result中有正确的profile
        if isinstance(analyzer.profile, dict):
            analysis_result['profile'] = analyzer.profile
        else:
            # 创建基本的profile字典
            analysis_result['profile'] = {
                'display_name': industry_display,
                'fundamental_rules': {},
                'risk_factors': ['行业政策风险', '市场竞争风险', '技术迭代风险'],
                'key_metrics_to_watch': [],
                'investment_themes': []
            }

        # 补充数据
        supplementary_data = {
            'ticker': ticker,
            'industry': industry,
            'industry_display': industry_display,
            'basic_info': stock_data.get('basic_info', {}),
            'financials': stock_data.get('financials', {}),
            'valuation': stock_data.get('valuation', {}),
            'price_data': stock_data.get('price_data', {}),
            'analyst': stock_data.get('analyst', {}),
            'current_price': stock_data.get('price_data', {}).get('latest', {}).get('current', 0),
            'company_dynamics': stock_data.get('company_dynamics', {}),
            'profile': analysis_result['profile']  # 使用已处理的profile
        }

        analysis_result['supplementary'] = supplementary_data

        # 生成TXT报告
        print(f"📄 生成报告中...")
        reporter = ReportGenerator(ticker, industry, analysis_result)
        report_content = reporter.generate()

        print(f"✅ 报告生成成功，长度: {len(report_content)} 字符")

        return {
            'success': True,
            'stock_data': stock_data,
            'analysis_result': analysis_result,
            'report_content': report_content,
            'ticker': ticker,
            'industry': industry,
            'industry_display': industry_display,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Streamlit分析失败: {str(e)}")
        print(f"详细错误:\n{error_details}")

        return {
            'success': False,
            'error': str(e),
            'error_details': error_details,
            'ticker': ticker
        }


def analyze_for_web(ticker, use_cache=True):
    """专为Web优化的分析函数"""
    try:
        # 1. 获取数据（与CLI相同）
        fetcher = UniversalDataFetcher(ticker, use_cache=use_cache)
        stock_data = fetcher.fetch_comprehensive_data()

        # 2. 确保技术数据足够
        stock_data = TechnicalDataEnhancer.ensure_sufficient_data(stock_data, min_days=60)

        # 3. 检测行业
        industry = detect_industry(ticker, stock_data)

        # 4. 基本面分析
        analyzer = UniversalAnalyzer(industry)
        analysis_result = analyzer.analyze(stock_data)

        # 5. 技术分析
        price_data = stock_data.get('price_data', {})
        tech_analyzer = AdvancedTechnicalAnalyzer(price_data)
        tech_indicators = tech_analyzer.calculate_all_indicators()
        analysis_result['technical_indicators'] = tech_indicators

        # 6. 关键步骤：准备完整的补充数据
        supplementary_data = {
            'ticker': ticker,
            'industry': industry,
            'basic_info': stock_data.get('basic_info', {}),
            'financials': stock_data.get('financials', {}),
            'valuation': stock_data.get('valuation', {}),
            'price_data': stock_data.get('price_data', {}),
            'analyst': stock_data.get('analyst', {}),
            'company_dynamics': stock_data.get('company_dynamics', {}),
            'profile': analyzer.profile if hasattr(analyzer, 'profile') else {},
        }

        # 添加当前价格
        latest_price = stock_data.get('price_data', {}).get('latest', {}).get('current', 0)
        supplementary_data['current_price'] = latest_price

        # 7. 将补充数据合并到analysis_result中
        # 使用update直接合并，而不是创建新键
        analysis_result.update({
            'supplementary': supplementary_data,
            'ticker': ticker,
            'industry': industry,
            'current_price': latest_price,
            'stock_data_snapshot': {  # 重要数据的快照
                'market_cap': stock_data.get('financials', {}).get('market_cap', 0),
                'revenue_growth': stock_data.get('financials', {}).get('revenue_growth', 0),
                'profit_margin': stock_data.get('financials', {}).get('profit_margin', 0),
                'debt_to_equity': stock_data.get('financials', {}).get('debt_to_equity', 0),
            }
        })

        # 8. 生成报告 - 使用完整的analysis_result
        reporter = ReportGenerator(ticker, industry, analysis_result)
        report_content = reporter.generate()

        return {
            'success': True,
            'analysis_result': analysis_result,
            'report_content': report_content,
            'ticker': ticker,
            'industry': industry,
            'data_quality': stock_data.get('data_quality', 'unknown')
        }

    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

if __name__ == "__main__":
    # 创建必要目录
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('data/cache', exist_ok=True)

    # 检查是否有命令行参数
    import sys

    if len(sys.argv) > 1:
        # 命令行模式
        ticker = sys.argv[1].upper()
        use_cache = len(sys.argv) > 2 and sys.argv[2].lower() != '--no-cache'

        print(f"🚀 命令行分析模式: {ticker}")
        print(f"💾 缓存: {'启用' if use_cache else '禁用'}")

        # 直接运行分析
        import asyncio

        try:
            # 显示快速示例
            quick_examples()

            # 运行主程序
            main()
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出")
        except Exception as e:
            print(f"\n❌ 程序错误: {e}")
    else:
        # 交互模式
        # 显示快速示例
        quick_examples()

        # 运行主程序
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出")
        except Exception as e:
            print(f"\n❌ 程序错误: {e}")