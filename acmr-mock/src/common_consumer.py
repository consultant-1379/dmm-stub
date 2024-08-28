import logging
from confluent_kafka import Consumer,KafkaError
from logger_config import logger
import configuration
import json

class MessageConsumeOauth:

    def __init__(self, broker, topic,group):
        self.broker = broker
        self.topic = topic
        self.group = group
    def error_callback(self,err):
        logger.error(f"Failed to connect kafka - {self.broker} - {err}")
        raise err

    def consumer_config(self,group):
        logger = logging.getLogger(__name__)
        config = {
            'group.id': group,
            'bootstrap.servers': self.broker ,
            'auto.offset.reset': 'earliest',
            'error_cb': self.error_callback ,
        }
        return config
    
    def consume_from_topic(self):
        consumer_conf = self.consumer_config(self.group)
        logger.info(f"Consumer configuration : {consumer_conf}")
        c = Consumer(consumer_conf)
        c.subscribe([self.topic])
        logger.info("Subscribing to topic")
        while True:
            msgs = c.poll()
            if msgs is None:
                continue
            if msgs.error():
                if msgs.error().code() == KafkaError._PARTITION_EOF:
                    print('End of partition reached')
                else:
                    print('Error: {}'.format(msgs.error().str()))
            else:
                value = json.loads(msgs.value().decode('utf-8'))
                return value