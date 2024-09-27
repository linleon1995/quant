from datetime import datetime

import pytest

from src.database_operator import ArcticDBOperator


@pytest.fixture
def mock_data_op():
    return ArcticDBOperator(url='lmdb://database', lib_name='Binance')


def test_read_db_data(mock_data_op):
    # normal case
    data = mock_data_op.read(data_name='WIFUSDT', date_range=(datetime(2024, 4, 5, 1, 16), datetime(2024, 4, 5, 2, 17)))
    data = mock_data_op.read(data_name='WIFUSDT', date_range=(datetime(2024, 9, 15, 1, 16), datetime(2024, 9, 15, 2, 17)))

    # wrong datetime format
    # mock_data_op.read(data_name='ETHUSDT', date_range=('2024-01-01', '2024-01-02'))
    pass

def test_read_new_data(mock_data_op):
    mock_data_op.read(data_name='ETHUSDT', date_range=('2024-01-01', '2024-01-02'))
