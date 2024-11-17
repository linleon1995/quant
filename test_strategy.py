import random
import time
from collections import deque
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd

from src.create_backtest_database import ArcticDBOperator


class SimpleMomentumStrategy:
    def __init__(self, short_window=3, long_window=10, base_threshold=0.001, stop_loss=0.02, 
                 take_profit=0.05, fee_rate=0.001, momentum_window=20, momentum_threshold_count=5):
        """
        初始化策略參數
        """
        self.short_window = short_window
        self.long_window = long_window
        self.base_threshold = base_threshold
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.fee_rate = fee_rate
        self.momentum_window = momentum_window
        self.momentum_threshold_count = momentum_threshold_count

        self.data_window_size = max(short_window, long_window, momentum_window)
        self.price_data = deque(maxlen=self.data_window_size)
        self.position = None  # "BUY", or None
        self.entry_price = None  # 持倉價格
        self.total_profit = 0.0  # 累積淨利潤
        self.momentum_signals = deque(maxlen=momentum_window)  # 儲存近期 momentum 信號
        self.momentum = None
        self.dynamic_threshold = None
    def add_price(self, price):
        """
        新增價格到資料窗口
        """
        self.price_data.append(price)

    def calculate_sma(self, window):
        """
        計算移動平均線
        """
        if len(self.price_data) < window:
            return None
        return sum(list(self.price_data)[-window:]) / window

    def calculate_momentum(self):
        """
        計算價格變化率
        """
        if len(self.price_data) < 2:
            return None
        prices = list(self.price_data)
        return (prices[-1] - prices[-2]) / prices[-2]

    def adjust_threshold(self):
        """
        動態調整動能閾值
        """
        if len(self.price_data) < self.data_window_size:
            return self.base_threshold

        # 使用價格變化率的標準差來調整
        prices = list(self.price_data)
        momentum_values = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]
        avg_momentum = sum(momentum_values) / len(momentum_values)
        adjusted_threshold = self.base_threshold + avg_momentum * 0.5
        return max(self.base_threshold, adjusted_threshold)  # 確保閾值不小於基準

    def update_momentum_signals(self, momentum, threshold):
        """
        更新 momentum 信號狀態
        """
        if momentum is None:
            return
        signal = 0
        if momentum > threshold:
            signal = 1  # 上漲信號
        elif momentum < -threshold:
            signal = -1  # 下跌信號

        self.momentum_signals.append(signal)

    def check_momentum_density(self):
        """
        檢查最近 momentum 窗口內信號密集程度
        """
        if len(self.momentum_signals) < self.momentum_window:
            return False

        # 計算正向與負向信號數量
        buy_signals = sum(1 for sig in self.momentum_signals if sig == 1)
        sell_signals = sum(1 for sig in self.momentum_signals if sig == -1)

        return buy_signals >= self.momentum_threshold_count or sell_signals >= self.momentum_threshold_count

    def check_stop_loss_or_take_profit(self, price):
        """
        判斷是否觸發止損或停利
        """
        if self.entry_price is None:
            return None

        # 計算價格變化百分比
        change_percentage = (price - self.entry_price) / self.entry_price

        if change_percentage <= -self.stop_loss:
            return "SELL"  # 止損
        # elif change_percentage >= self.take_profit:
        #     return "SELL"  # 停利
        return None

    def check_signal(self):
        """
        判斷交易信號
        """
        if len(self.price_data) < self.data_window_size:
            return None

        sma_short = self.calculate_sma(self.short_window)
        sma_long = self.calculate_sma(self.long_window)
        momentum = self.calculate_momentum()
        dynamic_threshold = self.adjust_threshold()

        if sma_short is None or sma_long is None or momentum is None:
            return None

        # 更新 momentum 信號
        self.update_momentum_signals(momentum, dynamic_threshold)

        # 停利與止損優先判斷
        price = self.price_data[-1]

        self.momentum = momentum
        self.dynamic_threshold = dynamic_threshold

        stop_signal = self.check_stop_loss_or_take_profit(price)
        if stop_signal:
            return stop_signal

        # 檢查 momentum 密集條件
        if not self.check_momentum_density():
            return None

        # 僅在空倉時允許買入
        if self.position is None and sma_short > sma_long and momentum > dynamic_threshold:
            return "BUY"
        # 僅在持倉時允許賣出
        # elif self.position == "BUY" and sma_short < sma_long and momentum < -dynamic_threshold:
        #     return "SELL"
        
        return None

    def execute_trade(self, signal, price):
        """
        執行交易
        """
        if signal == "BUY":
            self.position = "BUY"
            self.entry_price = price
            cost = price * self.fee_rate
            print(f"------Executed BUY at price {price} (Fee: {cost:.2f})")
        elif signal == "SELL":
            # 計算交易收益
            profit = price - self.entry_price
            net_profit = profit - (self.entry_price + price) * self.fee_rate
            self.total_profit += net_profit
            print(f"------Executed SELL at price {price} (Net Profit: {net_profit:.2f}, Total Profit: {self.total_profit:.2f})")
            self.position = None
            self.entry_price = None

    def on_new_price(self, price):
        """
        處理新價格數據
        """
        self.signal = None
        self.add_price(price)
        signal = self.check_signal()
        if signal:
            self.signal = signal
            self.execute_trade(signal, price)



def plot_price_with_signals(prices, timestamps, buy_signals, sell_signals):
    """
    繪製價格走勢圖，並標記 Buy 和 Sell 信號，X 軸顯示時間戳。
    
    :param prices: 價格數據 (list or pandas.Series)
    :param timestamps: 時間戳數據 (list or pandas.Series)
    :param buy_signals: Buy 信號的索引列表 (list of int)
    :param sell_signals: Sell 信號的索引列表 (list of int)
    """
    # 確保 timestamps 為 pandas.Timestamp 格式
    if not isinstance(timestamps[0], pd.DatetimeIndex):
        timestamps = pd.to_datetime(timestamps)

    # 創建圖表
    fig, ax = plt.subplots(figsize=(15, 5))

    # 繪製價格走勢圖
    ax.plot(timestamps, prices, label="Price", linewidth=1.5, color="blue")

    # 標記 Buy 信號
    for idx in buy_signals:
        ax.scatter(
            timestamps[idx], prices[idx], color="green", marker="^", s=200,
            label="Buy Signal" if idx == buy_signals[0] else ""
        )

    # 標記 Sell 信號
    for idx in sell_signals:
        ax.scatter(
            timestamps[idx], prices[idx], color="red", marker="v", s=200,
            label="Sell Signal" if idx == sell_signals[0] else ""
        )

    # 設置 X 軸為時間並自動格式化日期
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%Y-%m-%d %H:%M"))
    fig.autofmt_xdate()  # 自動旋轉 X 軸標籤

    # 加入標籤與圖例
    ax.set_title("Price Trend with Buy/Sell Signals")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True)
    plt.show()
    fig.savefig('test.png')

def test():
    # data
    coin_list = [
        'DOGEUSDT'
    ]
    start_time = datetime(2024, 1, 1, 0, 0)
    end_time = datetime(2024, 11, 15, 0, 0)
    total_time = {}
    arctic_ops = ArcticDBOperator(url="lmdb://arctic_database", lib_name='Binance')

    # strategy
    momentum_window = 10
    strategy = strategy = SimpleMomentumStrategy(
            short_window=3,
            long_window=10,
            base_threshold=0.004,
            stop_loss=0.1,
            take_profit=0.20,
            fee_rate=0.001,
            momentum_window=momentum_window
        )

    # Read data from database
    arctic_obj = arctic_ops.read(data_name=coin_list[0], start_time=start_time, end_time=end_time)
    dataset = arctic_obj.data
    prices, dyanmic_thresholds, momentums = [], [], []
    buy_signals, sell_signals = [], []
    for i, (timestamp, data) in enumerate(dataset.iterrows()):
        open_price = float(data['open_price'])
        strategy.on_new_price(open_price)
        if strategy.signal == 'BUY':
            buy_signals.append(i)
        elif strategy.signal == 'SELL':
            sell_signals.append(i)

        if strategy.dynamic_threshold is not None:
            dyanmic_thresholds.append(strategy.dynamic_threshold)
        if strategy.momentum is not None:
            momentums.append(strategy.momentum)
        prices.append(open_price)

        if i%100 == 0:
            print(f'{timestamp} - open_price: {open_price}')

    prices = prices[momentum_window-1:]
    timestamps = dataset.index[momentum_window-1:]
    plot_price_with_signals(prices, timestamps=timestamps, buy_signals=buy_signals, sell_signals=sell_signals)
    # fig, ax = plt.subplots(1, 1, figsize=(15, 5))
    # ax.plot(prices, label='price')
    # ax.plot(dyanmic_thresholds, label='threshold')
    # ax.plot(momentums, label='momentum')
    # ax.legend()
    # plt.show()
    pass

if __name__ == '__main__':
    test()