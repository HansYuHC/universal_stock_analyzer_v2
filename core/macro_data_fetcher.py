import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import yfinance as yf
from fredapi import Fred


class MacroDataFetcher:
    """宏观经济数据获取器"""

    def __init__(self, api_key=None):
        self.fred = Fred(api_key=api_key) if api_key else None

    def get_all_macro_indicators(self):
        """获取所有宏观经济指标"""
        print("📊 获取宏观经济数据...")

        macro_data = {
            'interest_rates': self._get_interest_rates(),
            'inflation': self._get_inflation_data(),
            'employment': self._get_employment_data(),
            'market_sentiment': self._get_market_sentiment(),
            'economic_indicators': self._get_economic_indicators(),
            'timestamp': datetime.now().isoformat(),
        }

        print(f"✅ 获取 {len(macro_data)} 个宏观数据维度")
        return macro_data

    def _get_interest_rates(self):
        """获取利率数据"""
        try:
            # 从FRED获取（如果有API密钥）
            if self.fred:
                fed_funds = self.fred.get_series('FEDFUNDS')
                ten_year = self.fred.get_series('DGS10')
                two_year = self.fred.get_series('DGS2')

                return {
                    'fed_funds_rate': float(fed_funds.iloc[-1]) if not fed_funds.empty else None,
                    '10y_treasury': float(ten_year.iloc[-1]) if not ten_year.empty else None,
                    '2y_treasury': float(two_year.iloc[-1]) if not two_year.empty else None,
                    'yield_curve': (float(ten_year.iloc[-1]) - float(two_year.iloc[-1]))
                    if not ten_year.empty and not two_year.empty else None,
                }

            # 备用方法：从Yahoo Finance获取
            ^ 10 = yf.Ticker("^TNX")  # 10年期国债
            ^ 2 = yf.Ticker("^FVX")  # 5年期国债（近似）

            ten_year_rate = ^ 10.
            info.get('regularMarketPrice', None)
            five_year_rate = ^ 2.
            info.get('regularMarketPrice', None)

            return {
                '10y_treasury': ten_year_rate,
                '5y_treasury': five_year_rate,
                'yield_curve': (ten_year_rate - five_year_rate)
                if ten_year_rate and five_year_rate else None,
                'source': 'Yahoo Finance',
            }

        except:
            return {'error': '无法获取利率数据'}

    def _get_inflation_data(self):
        """获取通胀数据"""
        try:
            # CPI数据
            cpi_ticker = yf.Ticker("CPIAUCSL")
            cpi_history = cpi_ticker.history(period="1y")

            if not cpi_history.empty:
                latest_cpi = cpi_history['Close'].iloc[-1]
                prev_cpi = cpi_history['Close'].iloc[-2] if len(cpi_history) > 1 else latest_cpi
                cpi_yoy = (latest_cpi / prev_cpi - 1) * 100
            else:
                cpi_yoy = None

            # PPI数据
            ppi_ticker = yf.Ticker("PPIACO")
            ppi_history = ppi_ticker.history(period="1y")

            if not ppi_history.empty:
                latest_ppi = ppi_history['Close'].iloc[-1]
                prev_ppi = ppi_history['Close'].iloc[-2] if len(ppi_history) > 1 else latest_ppi
                ppi_yoy = (latest_ppi / prev_ppi - 1) * 100
            else:
                ppi_yoy = None

            return {
                'cpi_yoy': cpi_yoy,
                'ppi_yoy': ppi_yoy,
                'inflation_trend': 'rising' if cpi_yoy and cpi_yoy > 2 else 'stable',
            }
        except:
            return {'error': '无法获取通胀数据'}

    def _get_employment_data(self):
        """获取就业数据"""
        try:
            # 失业率
            unrate_ticker = yf.Ticker("UNRATE")
            unrate_history = unrate_ticker.history(period="1y")

            if not unrate_history.empty:
                unemployment_rate = unrate_history['Close'].iloc[-1]
            else:
                unemployment_rate = None

            # 非农就业
            payroll_ticker = yf.Ticker("PAYEMS")
            payroll_history = payroll_ticker.history(period="1y")

            if not payroll_history.empty:
                nonfarm_payrolls = payroll_history['Close'].iloc[-1]
                prev_payrolls = payroll_history['Close'].iloc[-2] if len(payroll_history) > 1 else nonfarm_payrolls
                payroll_change = nonfarm_payrolls - prev_payrolls
            else:
                payroll_change = None

            return {
                'unemployment_rate': unemployment_rate,
                'nonfarm_payroll_change': payroll_change,
                'labor_market': 'tight' if unemployment_rate and unemployment_rate < 4 else 'normal',
            }
        except:
            return {'error': '无法获取就业数据'}

    def _get_market_sentiment(self):
        """获取市场情绪指标"""
        try:
            # VIX恐慌指数
            vix = yf.Ticker("^VIX")
            vix_price = vix.history(period="1d")['Close'].iloc[-1] if not vix.history(period="1d").empty else None

            # 恐慌贪婪指数（通过CNN）
            try:
                response = requests.get("https://money.cnn.com/data/fear-and-greed/", timeout=5)
                # 这里需要解析HTML，简化处理
                fear_greed = "N/A"
            except:
                fear_greed = "N/A"

            # 看跌看涨比率
            pcr_ticker = yf.Ticker("PCRATIO")
            pcr_data = pcr_ticker.history(period="1d")
            put_call_ratio = pcr_data['Close'].iloc[-1] if not pcr_data.empty else None

            return {
                'vix_index': vix_price,
                'fear_greed_index': fear_greed,
                'put_call_ratio': put_call_ratio,
                'market_sentiment': 'fearful' if vix_price and vix_price > 25 else 'greedy' if vix_price and vix_price < 15 else 'neutral',
            }
        except:
            return {'error': '无法获取市场情绪数据'}

    def _get_economic_indicators(self):
        """获取其他经济指标"""
        try:
            # GDP增长率
            gdp_ticker = yf.Ticker("GDP")
            gdp_data = gdp_ticker.history(period="1y")
            gdp_growth = gdp_data['Close'].pct_change().iloc[-1] * 100 if not gdp_data.empty else None

            # 制造业PMI
            pmi_ticker = yf.Ticker("ISM_MAN_PMI")
            pmi_data = pmi_ticker.history(period="1y")
            pmi = pmi_data['Close'].iloc[-1] if not pmi_data.empty else None

            # 消费者信心
            consumer_ticker = yf.Ticker("UMCSENT")
            consumer_data = consumer_ticker.history(period="1y")
            consumer_confidence = consumer_data['Close'].iloc[-1] if not consumer_data.empty else None

            return {
                'gdp_growth': gdp_growth,
                'manufacturing_pmi': pmi,
                'consumer_confidence': consumer_confidence,
                'recession_risk': 'low' if gdp_growth and gdp_growth > 1 and pmi and pmi > 50 else 'moderate',
            }
        except:
            return {'error': '无法获取经济指标'}