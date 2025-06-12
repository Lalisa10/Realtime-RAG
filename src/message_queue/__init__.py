from confluent_kafka import Producer, Consumer
from dotenv import load_dotenv
import os

def load_config():
    load_dotenv()
    # reads the client configuration from client.properties
    # and returns it as a key-value map
    config = {}
    with open("src/message_queue/client.properties") as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                config[parameter] = value.strip()
    config['sasl.username'] = os.getenv("CONFLUENT_API_KEY")
    config['sasl.password'] = os.getenv("CONFLUENT_API_SECRET")
    config['bootstrap.servers'] = os.getenv("CONFLUENT_BOOTSTRAP_SERVERS")
    return config
