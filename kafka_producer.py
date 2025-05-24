import asyncio
import json
import logging
from datetime import datetime

import websockets
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

logging.basicConfig(level=logging.INFO)

KAFKA_BOOTSTRAP_SERVERS = ['localhost:29092']  # 你的 Kafka 地址
KAFKA_TOPIC = 'binance_kline'  # 你要發送的 Topic 名稱
BINANCE_WS_URI = "wss://stream.binance.com:9443/ws"

# Create Kafka topic if it does not exist

def create_kafka_topic(topic_name, bootstrap_servers):
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    topic_list = admin_client.list_topics()
    if topic_name not in topic_list:
        topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
        try:
            admin_client.create_topics([topic])
            logging.info(f"Created Kafka topic: {topic_name}")
        except Exception as e:
            logging.warning(f"Could not create topic {topic_name}: {e}")
    admin_client.close()

create_kafka_topic(KAFKA_TOPIC, KAFKA_BOOTSTRAP_SERVERS)


class BinanceKafkaProducerService:
    def __init__(self, symbols):
        self.symbols = symbols  # e.g. ["btcusdt@kline_1m", "ethusdt@kline_1m"]
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.last_timestamps = {}
    
    async def connect_and_consume(self):
        async with websockets.connect(BINANCE_WS_URI) as ws:
            subscribe_msg = {
                "method": "SUBSCRIBE",
                "params": self.symbols,
                "id": 1
            }
            await ws.send(json.dumps(subscribe_msg))
            logging.info(f"Subscribed to Binance streams: {self.symbols}")

            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    if 'k' in data:
                        symbol = data['s']
                        kline = data['k']
                        timestamp = datetime.fromtimestamp(kline['T'] / 1000).strftime('%Y-%m-%d %H:%M:%S')

                        # 跳過重複的資料
                        if self.last_timestamps.get(symbol) == timestamp:
                            continue

                        self.last_timestamps[symbol] = timestamp

                        close_price = float(kline['c'])
                        tic = {
                            'timestamp': timestamp,
                            'symbol': symbol,
                            'close_price': close_price
                        }

                        self.producer.send(KAFKA_TOPIC, tic)
                        logging.debug(f"Sent: {tic}")

                except Exception as e:
                    logging.error(f"Error receiving or sending data: {e}")
                    await asyncio.sleep(5)

    def run(self):
        asyncio.run(self.connect_and_consume())
        

if __name__ == "__main__":
    # 你訂閱哪些幣種的 kline，格式 Binance 規定是小寫符號+@kline_時間周期
    symbols = [
        "btcusdt@kline_1m",
        "ethusdt@kline_1m",
        # 你想要的其他幣種
    ]

    service = BinanceKafkaProducerService(symbols)
    service.run()
