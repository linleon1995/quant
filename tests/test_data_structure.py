import pytest
from datetime import datetime

from src.data_process.data_structure import GeneralTickData


@pytest.fixture
def mock_general_tick_data():
    return GeneralTickData(symbol='BTCUSDT', maxlen=5, mean_average_spans=[1, 4])


def test_general_tick_data(mock_general_tick_data: GeneralTickData):
    now = datetime.now()
    mock_general_tick_data.put_tick(tick=0, unix_time=now)

    # test basic ticks and time function
    assert mock_general_tick_data.ticks[0] == 0
    assert mock_general_tick_data.time[0] == now

    # test mean average calculation
    mock_general_tick_data.put_tick(tick=100, unix_time=now)
    mock_general_tick_data.put_tick(tick=200, unix_time=now)
    mock_general_tick_data.put_tick(tick=300, unix_time=now)
    mock_general_tick_data.put_tick(tick=400, unix_time=now)
    mock_general_tick_data.put_tick(tick=500, unix_time=now)
    assert mock_general_tick_data.ticks[0] == 100
    assert mock_general_tick_data.ticks[-1] == 500
    assert mock_general_tick_data.mean_average_data_pool[1][-1] == 500
    assert mock_general_tick_data.mean_average_data_pool[4][-1] == 1400 / 4

    # test queue max length adjustment
    test_tick = GeneralTickData(symbol='BTCUSDT', maxlen=3, mean_average_spans=[100])
    assert test_tick.maxlen == 100