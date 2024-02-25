from pathlib import Path

from scipy.signal import find_peaks
import numpy as np


class Strategy:
    def __init__(self, reverse=True):
        self.strategy_name = Path(__file__).name
        self.reverse = reverse

    def run(self, data):
        if self.reverse:
            data = -np.array(data)
        peaks = find_peaks(data.raw_data)