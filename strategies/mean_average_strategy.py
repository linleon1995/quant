import numpy as np


class Strtegy:
    def __init__(self, time_periords, diff_rate, growth, acc_steps):
        self.time_periords = time_periords
        self.diff_rate = diff_rate
        self.growth = growth
        self.acc_steps = acc_steps
        self.achieve_count = 0
        self.last_sma_data = {}

    def run(self, data, symbol):
        judge, sma_data = self.cal_ma_diff(data)
        if judge:
            self.achieve_count += 1
            if symbol not in self.last_sma_data:
                self.last_sma_data[symbol] = sma_data
                growing = [True]
            else:
                growing = []
                for cur_sma, last_sma in zip(sma_data, self.last_sma_data[symbol]):
                    growing.append(cur_sma > last_sma*self.growth)
            if self.achieve_count >= self.acc_steps and all(growing):
                self.achieve_count = 0
                return True
        else:
            self.achieve_count = 0
        return False

    def cal_ma_diff(self, data):
        sma_data = {}
        for t in self.time_periords:
            sma = np.mean(data[-t:])
            sma_data[t] = sma
        
        sma_data = [sma_data[key] for key in sorted(sma_data.keys(), reverse=True)]

        last_sma = sma_data[0]
        judge = []
        for sma, r in zip(sma_data[1:], self.diff_rate):
            judge.append(sma > r*last_sma)
            last_sma = sma
        # print(sma_data)
        return all(judge), sma_data

