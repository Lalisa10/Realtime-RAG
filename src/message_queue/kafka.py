from . import load_config
from confluent_kafka import Producer, Consumer
import json

config = load_config()

def produce(topic, value, key=None):
    # creates a new producer instance
    producer = Producer(config)

    # produces a sample message
    producer.produce(topic, key=key, value=value)

    #key_str = key if key is not None else "None"
    #value_str = json.loads(value.e('utf-8'))
    #print(f"Produced message to topic {topic}: key = {key_str} value = {value_str}")

    # send any outstanding or buffered messages to the Kafka broker
    producer.flush()

def consume(topic):
    # sets the consumer group ID and offset
    config["group.id"] = "python-group-1"
    config["auto.offset.reset"] = "earliest"

    # creates a new consumer instance
    consumer = Consumer(config)

    # subscribes to the specified topic
    consumer.subscribe([topic])

    try:
        while True:
            # consumer polls the topic and prints any incoming messages
            msg = consumer.poll(1.0)
            if msg is not None and msg.error() is None:
                key = msg.key().decode("utf-8")
                value = msg.value().decode("utf-8")
                print(f"Consumed message from topic {topic}: key = {key} value = {value}")
    except KeyboardInterrupt:
        pass
    finally:
    # closes the consumer connection
        consumer.close()

def main():
    produce("rag_embeddings", "abcxyz", "abc")
    
if __name__ == "__main__":
    main()