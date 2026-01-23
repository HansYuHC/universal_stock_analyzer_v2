import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class StrategyBacktester:
    """策略回测引擎"""

    def __init__(self, price_data, initial_capital=10000):
        self.price_data = price_data
        self.initial_capital = initial_capital
        self.df = price_data.get('history', pd.DataFrame()).copy()

    def backtest_strategy(self, strategy_type='dual_momentum'):
        """回测指定策略"""
        if self.df.empty or len(self.df) < 100:
            return {"error": "数据不足进行回测"}

        print(f"🔍 开始回测 {strategy_type} 策略...")

        strategies = {
            'dual_momentum': self._dual_momentum_strategy,
            'mean_reversion': self._mean_reversion_strategy,
            'trend_following': self._trend_following_strategy,
            'breakout': self._breakout_strategy,
        }

        strategy_func = strategies.get(strategy_type, self._dual_momentum_strategy)
        return strategy_func()

    def _dual_momentum_strategy(self):
        """双动量策略回测"""
        df = self.df.copy()

        # 计算动量指标
        df['Returns'] = df['Close'].pct_change()
        df['Momentum_1M'] = df['Close'].pct_change(21)  # 1个月动量
        df['Momentum_3M'] = df['Close'].pct_change(63)  # 3个月动量
        df['Volatility_20D'] = df['Returns'].rolling(20).std() * np.sqrt(252)

        # 生成交易信号
        df['Signal'] = 0

        # 买入条件：双动量为正且波动率适中
        buy_condition = (
                (df['Momentum_1M'] > 0.02) &
                (df['Momentum_3M'] > 0.05) &
                (df['Volatility_20D'] < 0.4)
        )

        # 卖出条件：动量转负或波动率过高
        sell_condition = (
                (df['Momentum_1M'] < -0.01) |
                (df['Volatility_20D'] > 0.5)
        )

        df.loc[buy_condition, 'Signal'] = 1
        df.loc[sell_condition, 'Signal'] = -1

        # 模拟交易
        capital = self.initial_capital
        position = 0
        trades = []
        equity_curve = []

        for i in range(1, len(df)):
            current_price = df['Close'].iloc[i]
            signal = df['Signal'].iloc[i]

            # 执行交易
            if signal == 1 and position == 0:  # 买入
                position = capital / current_price
                capital = 0
                trades.append({
                    'date': df.index[i],
                    'action': 'BUY',
                    'price': current_price,
                    'shares': position
                })
            elif signal == -1 and position > 0:  # 卖出
                capital = position * current_price
                position = 0
                trades.append({
                    'date': df.index[i],
                    'action': 'SELL',
                    'price': current_price,
                    'shares': position
                })

            # 计算当前权益
            current_equity = capital + (position * current_price if position > 0 else 0)
            equity_curve.append(current_equity)

        # 计算绩效指标
        final_equity = equity_curve[-1] if equity_curve else self.initial_capital
        total_return = (final_equity / self.initial_capital - 1) * 100

        # 买持有策略对比
        buy_hold_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100

        return {
            'strategy_name': '双动量策略',
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return_pct': total_return,
            'annualized_return': self._calculate_annualized_return(equity_curve),
            'max_drawdown': self._calculate_max_drawdown(equity_curve),
            'sharpe_ratio': self._calculate_sharpe_ratio(equity_curve),
            'win_rate': self._calculate_win_rate(trades),
            'total_trades': len(trades),
            'buy_hold_return': buy_hold_return,
            'outperformance': total_return - buy_hold_return,
            'trades': trades[-10:],  # 最近10笔交易
            'equity_curve': equity_curve[-100:],  # 最近100个权益点
        }

    # 其他策略实现...
    def _mean_reversion_strategy(self):
        """均值回归策略"""
        # 实现类似上面的策略
        pass

    def _trend_following_strategy(self):
        """趋势跟踪策略"""
        pass

    def _breakout_strategy(self):
        """突破策略"""
        pass

    def _calculate_annualized_return(self, equity_curve):
        """计算年化收益率"""
        if len(equity_curve) < 2:
            return 0

        total_return = equity_curve[-1] / equity_curve[0] - 1
        years = len(equity_curve) / 252  # 假设252个交易日
        return ((1 + total_return) ** (1 / years) - 1) * 100 if years > 0 else 0

    def _calculate_max_drawdown(self, equity_curve):
        """计算最大回撤"""
        if len(equity_curve) < 2:
            return 0

        peak = equity_curve[0]
        max_dd = 0

        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _calculate_sharpe_ratio(self, equity_curve):
        """计算夏普比率"""
        if len(equity_curve) < 2:
            return 0

        returns = pd.Series(equity_curve).pct_change().dropna()
        if len(returns) < 2:
            return 0

        excess_returns = returns - 0.02 / 252  # 假设无风险利率2%
        sharpe = np.sqrt(252) * excess_returns.mean() / returns.std() if returns.std() > 0 else 0
        return sharpe

    def _calculate_win_rate(self, trades):
        """计算胜率"""
        if len(trades) < 4:  # 需要至少2次完整买卖
            return 0

        # 计算盈利交易比例
        wins = 0
        total_pairs = len(trades) // 2

        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades):
                buy_trade = trades[i]
                sell_trade = trades[i + 1]
                if sell_trade['price'] > buy_trade['price']:
                    wins += 1

        return (wins / total_pairs * 100) if total_pairs > 0 else 0