import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_random_data(num_rows):
    # Generate random timestamps
    start_time = datetime(2024, 3, 5, 14, 0, 0)
    time_deltas = [timedelta(days=i) for i in range(num_rows)]
    timestamps = [start_time + delta for delta in time_deltas]
    end_time = timestamps[-1]

    # Generate random data
    open_prices = np.random.uniform(1.5, 2.0, num_rows)
    high_prices = open_prices + np.random.uniform(0.1, 0.5, num_rows)
    low_prices = open_prices - np.random.uniform(0.1, 0.5, num_rows)
    close_prices = np.random.uniform(low_prices, high_prices)
    volumes = np.random.uniform(1e6, 5e6, num_rows)
    quote_asset_volumes = np.random.uniform(1e6, 5e6, num_rows)
    number_of_trades = np.random.randint(1000, 30000, num_rows)
    taker_buy_base_asset_volumes = np.random.uniform(1e5, 1e6, num_rows)
    taker_buy_quote_asset_volumes = np.random.uniform(1e5, 1e6, num_rows)

    # Construct the DataFrame
    df = pd.DataFrame({
        'open_time': timestamps,
        'open_price': open_prices,
        'high_price': high_prices,
        'low_price': low_prices,
        'close_price': close_prices,
        'volume': volumes,
        'close_time': [ts + timedelta(minutes=1) for ts in timestamps],
        'quote_asset_volume': quote_asset_volumes,
        'number_of_trades': number_of_trades,
        'taker_buy_base_asset_volume': taker_buy_base_asset_volumes,
        'taker_buy_quote_asset_volume': taker_buy_quote_asset_volumes,
        'unused_field': np.zeros(num_rows)  # Assuming 'unused_field' is just a placeholder
    })

    return df, start_time, end_time

