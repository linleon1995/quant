import asyncio
import websockets
import json

from binance_api import get_usdt_ticker


async def subscribe_to_klines():
    uri = "wss://stream.binance.com:9443/ws"

    
    ticker_prices = get_usdt_ticker(bridge='USDT')
    ticker_prices = ticker_prices[:10]
    symbols = [f"{coin['symbol'].lower()}@kline_1m" for idx, coin in enumerate(ticker_prices)]

    # subscribe_message = {
    #     "method": "UNSUBSCRIBE",
    #     "params": ["!ticker@arr"],
    #     "id": 1
    # }
    # subscribe_message = {
    #     "method": "LIST_SUBSCRIPTIONS",
    #     "id": 1
    # }
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params": symbols,
        "id": 1
    }

    async with websockets.connect(uri) as websocket:
        # Subscribe to the stream
        await websocket.send(json.dumps(subscribe_message))
        all_symbols = {}
        
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)



            # # Process the received data as needed
            # # print(response_data)
            # # if isinstance(response_data, dict):
            # if response_data.get('result', True) is not None:
            #     # for coin in response_data:
            #     # if 
            #     if response_data['s'] not in all_symbols and response_data['s'].endswith('USDT'):
            #         all_symbols[response_data['s']] = None
            #         print(len(all_symbols))
            #         if len(all_symbols) == 373:
            #             print(set(ticker_prices)-set(list(all_symbols.keys())))
            #             print(30*'-')
            #             print(all_symbols)
            # else:
            #     continue
            
            # print(response_data)

            # # Check if it's a miniTicker array update
            # if isinstance(response_data, list):
            #     for coin in response_data:
            #         if coin['s'] not in all_symbols and coin['s'].endswith('USDT'):
            #             all_symbols[coin['s']] = None
            #             print(len(all_symbols))
            # else:
            #     continue


async def subscribe_to_mini_ticker_arr():
    uri = "wss://stream.binance.com:9443/ws/!ticker@arr"

    subscribe_message = {
        "method": "SUBSCRIBE",
        "params": ["!ticker@arr"],
        # "params": ["!miniTicker@arr"],
        "id": 1
    }

    async with websockets.connect(uri) as websocket:
        # Subscribe to the stream
        await websocket.send(json.dumps(subscribe_message))
        all_symbols = {}
        
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)

            # Check if it's a miniTicker array update
            if isinstance(response_data, list):
                for coin in response_data:
                    if coin['s'] not in all_symbols and coin['s'].endswith('USDT'):
                        all_symbols[coin['s']] = None
                        print(len(all_symbols))
            else:
                continue

            # if 'e' in response_data[0] and response_data[0]['e'] == '24hrMiniTicker':
            #     mini_tickers = response_data['data']
            #     for mini_ticker in mini_tickers:
            #         symbol = mini_ticker['s']
            #         close_price = mini_ticker['c']
            #         volume = mini_ticker['v']
            #         print(f"Symbol: {symbol}, Close Price: {close_price}, Volume: {volume}")

async def main():
    await subscribe_to_klines()
    # await subscribe_to_mini_ticker_arr()

asyncio.get_event_loop().run_until_complete(main())
