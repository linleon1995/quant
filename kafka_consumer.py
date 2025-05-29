import json
import logging
from datetime import datetime

from kafka import KafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = ['localhost:29092']
KAFKA_TOPIC = 'binance_kline'

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/kafka_consumer.log"),
        logging.StreamHandler()
    ]
)

def parse_kafka_message(message_value):
    try:
        # Kafka message is in bytes -> decode -> json.loads
        msg_str = message_value.decode('utf-8')
        data = json.loads(msg_str)
        return data
    except Exception as e:
        logging.error(f"Error parsing message: {e}")
        return None

def consume_kafka_messages():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda v: v  # we decode manually
    )
    logging.info(f"Subscribed to Kafka topic: {KAFKA_TOPIC}")

    for msg in consumer:
        raw_data = parse_kafka_message(msg.value)
        if not raw_data:
            continue

        try:
            timestamp = raw_data['timestamp']
            symbol = raw_data['symbol']
            close_price = raw_data['close_price']

            # readable_time = datetime.fromtimestamp(timestamp / 1000)
            logging.info(f"{timestamp} - {symbol} Close Price: {close_price}")
        except KeyError as e:
            logging.warning(f"Incomplete data in message: {raw_data}")


if __name__ == "__main__":
    consume_kafka_messages()
