from unicorn_binance_websocket_api import BinanceWebSocketApiManager

ubwa = BinanceWebSocketApiManager(exchange="binance.com")
ubwa.create_stream(channels=['trade', 'kline_1m'], markets=['btcusdt', 'bnbbtc', 'ethbtc'])


while True:
    oldest_data_from_stream_buffer = ubwa.pop_stream_data_from_stream_buffer()
    if oldest_data_from_stream_buffer:
        print(oldest_data_from_stream_buffer)