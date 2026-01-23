import pandas as pd
import numpy as np
import ta
from datetime import datetime


class AdvancedTechnicalAnalyzer:
    """修复版技术分析器 - 处理金融股"""

    def __init__(self, price_data):
        self.price_data = price_data
        self.df = price_data.get('history', pd.DataFrame())
        self.is_financial = price_data.get('is_financial', False)
        self.has_sufficient_data = price_data.get('has_sufficient_data', False)

    def _prepare_dataframe(self, price_data):
        """准备DataFrame，确保格式正确"""
        history = price_data.get('history', None)

        if isinstance(history, pd.DataFrame) and not history.empty:
            # 确保有正确的列
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']

            # 如果缺少某些列，尝试补充
            for col in required_columns:
                if col not in history.columns:
                    if col == 'Close':
                        history[col] = history.get('Adj Close', history.get('close', 100))
                    elif col == 'Volume':
                        history[col] = 1000000  # 默认值
                    else:
                        # 对于OHL，基于Close估算
                        if col == 'Open':
                            history[col] = history['Close'] * np.random.uniform(0.98, 1.02, len(history))
                        elif col == 'High':
                            history[col] = history['Close'] * np.random.uniform(1.00, 1.04, len(history))
                        elif col == 'Low':
                            history[col] = history['Close'] * np.random.uniform(0.96, 1.00, len(history))

            return history.sort_index()

        # 如果历史数据无效，创建模拟数据
        latest_price = price_data.get('latest', {}).get('current', 100)
        print(f"⚠️  价格数据无效，创建模拟数据（最新价格: ${latest_price:.2f})")
        return self._create_simulated_data(latest_price)

    def _create_simulated_data(self, latest_price, days=60):
        """创建模拟数据用于技术分析"""
        np.random.seed(int(datetime.now().timestamp() % 10000))

        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

        # 随机价格路径
        returns = np.random.normal(0.0002, 0.02, days)  # 微小正趋势，2%波动

        prices = [latest_price]
        for i in range(1, days):
            new_price = prices[-1] * (1 + returns[i])
            prices.append(max(0.01, new_price))  # 防止负价格

        # 创建OHLCV数据
        data = {
            'Open': [p * np.random.uniform(0.99, 1.01) for p in prices],
            'High': [p * np.random.uniform(1.00, 1.03) for p in prices],
            'Low': [p * np.random.uniform(0.97, 1.00) for p in prices],
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, days),
        }

        df = pd.DataFrame(data, index=dates)
        df.index.name = 'Date'

        return df

    def calculate_all_indicators(self):
        """计算所有技术指标（适应金融股）"""
        if self.df.empty or len(self.df) < 10:
            return self._get_basic_indicators()

        try:
            results = {}
            results['trend'] = self._calculate_trend_indicators()
            results['momentum'] = self._calculate_momentum_indicators()
            results['volatility'] = self._calculate_volatility_indicators()
            results['signals'] = self._generate_technical_signals(results)

            # 金融股特别调整
            if self.is_financial:
                results = self._adjust_for_financial_stock(results)

            return results

        except Exception as e:
            print(f"技术指标计算失败: {e}")
            return self._get_basic_indicators()

    def _get_basic_indicators(self):
        """获取基础指标（当数据不足时）"""
        # 尝试从price_data获取技术指标
        technicals = self.price_data.get('technicals', {})

        if technicals.get('can_calculate', False):
            rsi = technicals.get('rsi', 50)
            ma20 = technicals.get('ma20', 100)
            ma50 = technicals.get('ma50', 100)
        else:
            # 使用默认值
            rsi = 50
            ma20 = self.price_data.get('latest', {}).get('current', 100)
            ma50 = ma20

        return {
            'trend': {
                'macd_signal': 'neutral',
                'bb_position': 0.5,
                'trend_strength': 'moderate',
                'message': '基于基础数据计算',
            },
            'momentum': {
                'rsi_14': rsi,
                'stoch_k': 50,
                'oversold': rsi < 30,
                'overbought': rsi > 70,
                'data_status': 'basic',
            },
            'volatility': {
                'atr_percent': 2.0,  # 默认2%
                'volatility_20d': 20.0,
            },
            'signals': {
                'signals': ['使用基础技术指标'],
                'overall_signal': '中性',
                'confidence': 40,
            }
        }

    def _calculate_trend_indicators(self):
        """计算趋势指标"""
        df = self.df.copy()

        # 只有足够数据时才计算复杂指标
        if len(df) < 30:
            return {
                'macd_signal': 'neutral',
                'bb_position': 0.5,
                'ma_cross': ['数据不足'],
                'trend_strength': 'insufficient_data',
            }

        # MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()

        # 布林带
        bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Middle'] = bb.bollinger_mavg()
        df['BB_Lower'] = bb.bollinger_lband()
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])

        latest = df.iloc[-1]

        return {
            'macd_signal': 'bullish' if latest['MACD'] > latest['MACD_Signal'] else 'bearish',
            'bb_position': float(latest['BB_Position']),
            'ma_cross': self._check_ma_cross(df),
            'trend_strength': self._calculate_trend_strength(df),
        }

    def _calculate_momentum_indicators(self):
        """计算动量指标"""
        df = self.df.copy()

        if len(df) < 20:
            return {
                'rsi_14': 50,
                'stoch_k': 50,
                'oversold': False,
                'overbought': False,
            }

        # RSI
        df['RSI_14'] = ta.momentum.rsi(df['Close'], window=14)

        # 随机指标
        stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'])
        df['Stoch_K'] = stoch.stoch()

        latest = df.iloc[-1]

        return {
            'rsi_14': float(latest['RSI_14']) if not pd.isna(latest['RSI_14']) else 50,
            'stoch_k': float(latest['Stoch_K']) if not pd.isna(latest['Stoch_K']) else 50,
            'oversold': (latest['RSI_14'] < 30 if not pd.isna(latest['RSI_14']) else False) or
                        (latest['Stoch_K'] < 20 if not pd.isna(latest['Stoch_K']) else False),
            'overbought': (latest['RSI_14'] > 70 if not pd.isna(latest['RSI_14']) else False) or
                          (latest['Stoch_K'] > 80 if not pd.isna(latest['Stoch_K']) else False),
        }

    def _calculate_volatility_indicators(self):
        """计算波动率指标"""
        df = self.df.copy()

        if len(df) < 20:
            return {
                'atr_percent': 0,
                'volatility_20d': 0,
            }

        # ATR
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])

        # 波动率
        returns = df['Close'].pct_change()
        df['Volatility_20d'] = returns.rolling(20).std() * np.sqrt(252) * 100

        latest = df.iloc[-1]

        return {
            'atr_percent': float(latest['ATR'] / latest['Close'] * 100) if latest['Close'] > 0 else 0,
            'volatility_20d': float(latest['Volatility_20d']) if not pd.isna(latest['Volatility_20d']) else 0,
        }

    def _check_ma_cross(self, df):
        """检查均线交叉"""
        if len(df) < 30:
            return ["数据不足"]

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        signals = []
        if prev['Close'] <= df['Close'].rolling(20).mean().iloc[-2] and latest['Close'] > \
                df['Close'].rolling(20).mean().iloc[-1]:
            signals.append("价格上穿20日均线")

        return signals if signals else ["无显著交叉"]

    def _calculate_trend_strength(self, df):
        """计算趋势强度"""
        if len(df) < 50:
            return "数据不足"

        # 简化趋势判断
        price_trend = "横盘"
        if len(df) >= 20:
            recent_change = (df['Close'].iloc[-1] / df['Close'].iloc[-20] - 1) * 100
            if recent_change > 5:
                price_trend = "短期上升"
            elif recent_change < -5:
                price_trend = "短期下降"

        return price_trend

    def _generate_technical_signals(self, all_indicators):
        """生成技术信号"""
        signals = []
        score = 0

        # RSI信号
        rsi = all_indicators['momentum']['rsi_14']
        if rsi < 30:
            signals.append("RSI超卖")
            score += 1
        elif rsi > 70:
            signals.append("RSI超买")
            score -= 1

        # 趋势信号
        trend_strength = all_indicators['trend']['trend_strength']
        if "上升" in trend_strength:
            score += 0.5
        elif "下降" in trend_strength:
            score -= 0.5

        # 综合信号
        if score >= 1:
            overall_signal = "看涨"
        elif score <= -1:
            overall_signal = "看跌"
        else:
            overall_signal = "中性"

        return {
            'signals': signals,
            'overall_signal': overall_signal,
            'confidence': min(abs(score) * 30, 80),  # 限制信心度
        }

    def _adjust_for_financial_stock(self, results):
        """调整金融股技术指标"""
        # 金融股技术分析权重较低
        if 'signals' in results:
            results['signals']['note'] = '金融股技术分析参考性较低'
            results['signals']['confidence'] = max(results['signals']['confidence'] * 0.7, 20)

        return results