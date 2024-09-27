from datetime import datetime

from src.ticker import Ticker
from src.database_operator import ArcticDBOperator


def test_ticker():
    mock_data_op = ArcticDBOperator(url='lmdb://database', lib_name='Binance')
    wifusdt_ticker = Ticker(database_op=mock_data_op, 
                            symbol='WIFUSDT', 
                            start_time=datetime(2024, 4, 1, 0, 0), 
                            end_time= datetime(2024, 7, 14, 16, 17), 
                            interval='1m')
    data = next(wifusdt_ticker)
    assert data is not None

    # data not exist
    # For persistant testing, remove the data and test then add the data back
    ethusdt_ticker = Ticker(database_op=mock_data_op, 
                            symbol='ETHUSDT', 
                            start_time=datetime(2024, 4, 1, 0, 0), 
                            end_time= datetime(2024, 7, 14, 16, 17), 
                            interval='1m')
    data = next(ethusdt_ticker)
    assert data is not None
    