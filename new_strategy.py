import numpy as np
import pandas as pd
from collections import deque

class DynamicBreakoutTrader:
    def __init__(self, lookback=14, pr_x=0.8, pr_y=0.7, atr_period=14, max_risk=0.02, leverage=1, adx_period=14):
        self.lookback = lookback  # 天數窗口
        self.pr_x = pr_x  # 進場百分比
        self.pr_y = pr_y  # 停損百分比
        self.atr_period = atr_period  # ATR 計算天數
        self.max_risk = max_risk  # 單筆交易最大風險（資本百分比）
        self.leverage = leverage  # 槓桿倍數
        self.adx_period = adx_period  # ADX 計算週期
        
        self.prices = deque(maxlen=lookback)  # 存歷史價格
        self.highs = deque(maxlen=lookback)
        self.lows = deque(maxlen=lookback)
        self.volumes = deque(maxlen=lookback)
        self.atr_values = deque(maxlen=atr_period)  # 存 ATR
        self.adx_values = deque(maxlen=adx_period)  # 存 ADX
        self.positions = []  # 目前持倉
        self.capital = 100000  # 初始資金
        self.current_atr = None  # 當前 ATR
        self.max_trade = 1
        self.num_trade = 0
        self.high = None
        self.low = None
        self.short_high = None
        self.short_low = None
        self.short_time_len = 120
        self.trade_records = []
        if self.lookback < self.short_time_len:
            raise ValueError("lookback should be larger than short_time_len")
    
    def _calculate_atr(self):
        if len(self.atr_values) < self.atr_period:
            return None
        return np.mean(self.atr_values)
    
    def _calculate_adx(self):
        if len(self.adx_values) < self.adx_period:
            return None
        return np.mean(self.adx_values)
    
    def on_tick(self, timestamp, data):
        price = float(data['close_price'])
        volume = float(data['volume'])

        self.prices.append(price)
        self.volumes.append(volume)
        
        if len(self.prices) < self.lookback:
            return  # 需要足夠的歷史數據
        
        # 計算唐奇安通道
        # TODO: relatively slow
        if self.high is None:
            self.high = max(self.prices)
        if self.low is None:
            self.low = min(self.prices)

        self.high = max(self.high, price)
        self.low = min(self.low, price)
        # high = max(self.prices)
        # low = min(self.prices)
        range_size = self.high - self.low
        
        # 計算 ATR
        if len(self.atr_values) >= 1:
            self.atr_values.append(abs(price - self.prices[-2]))
        self.current_atr = self._calculate_atr()
        
        # 計算 ADX（簡單版）
        if len(self.highs) >= 2:
            tr = max(self.highs[-1] - self.lows[-1], abs(self.highs[-1] - self.prices[-2]), abs(self.lows[-1] - self.prices[-2]))
            self.adx_values.append(tr)
        current_adx = self._calculate_adx()
        
        # 動態調整 PR X & PR Y
        dynamic_x = self.high - self.current_atr * self.pr_x if self.current_atr else self.high
        dynamic_y = self.low + self.current_atr * self.pr_y if self.current_atr else self.low
        
        # 進場條件：突破上通道 & 成交量確認 & ADX 趨勢強度
        if price >= dynamic_x and volume > np.mean(list(self.volumes)) and (current_adx is None or current_adx > 25) \
            and len(self.positions) <= self.max_trade:
            risk_amount = self.capital * self.max_risk
            position_size = risk_amount / self.current_atr if self.current_atr else 1
            position_size *= self.leverage
            self.positions.append({'entry': price, 'size': position_size, 'entry_time': timestamp})
            print(f"{timestamp} BUY at {price}, size {position_size}, ADX {current_adx}")
        
        # 出場條件
        # TODO: sell strategy
        if len(self.prices) > self.short_time_len:
            if self.short_high is None:
                self.short_high = max(list(self.prices))
            if self.short_low is None:
                self.short_low = min(list(self.prices))
            self.short_high = max(self.short_high, price)
            self.short_low = min(self.short_low, price)

        drawback = 0.05
        stop_trade_time_len = 60

        for pos in self.positions:
            if price < self.short_high * (1-drawback) \
                and (timestamp - pos['entry_time']).total_seconds() / 60 > stop_trade_time_len \
                and price > pos['entry']:
                print(f"{timestamp} EXIT WIN at {price}, size {pos['size']}")
                earn = (price - pos['entry']) / pos['entry'] * pos['size']
                self.trade_records.append({'earn': earn, 'entry': pos['entry'], 'exit': price, 
                                           'size': pos['size'], 'entry_time': pos['entry_time'], 'exit_time': timestamp})
                self.positions.remove(pos)
            elif price < self.short_low * (1-drawback):
                print(f"{timestamp} EXIT LOSS at {price}, size {pos['size']}")
                earn = (price - pos['entry']) / pos['entry'] * pos['size']
                self.trade_records.append({'earn': earn, 'entry': pos['entry'], 'exit': price, 
                                           'size': pos['size'], 'entry_time': pos['entry_time'], 'exit_time': timestamp})
                self.positions.remove(pos)