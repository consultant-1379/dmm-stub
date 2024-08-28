
import logging
from functools import partial
import time
from uuid import uuid4
import requests
import datetime
import threading
from confluent_kafka import Producer
from confluent_kafka.error import ProduceError
from logger_config import logger
from flask import abort
from queue import Queue
import numpy as np
import json
class MessageProduceOauth:

    def __init__(self, broker, topic):
        self.broker = broker
        self.topic = topic
    def error_callback(self,err):
        logger.error(f" Failed to connect kafka - {self.broker} - {err}")
        raise err


    def delivery_report(self, err, msg):
        if err:
            raise Exception(f" Delivery failed for Produce record at  {msg.key()}: {err}")
            
    def producer_config(self):
        config = {
            'bootstrap.servers': self.broker,
            'linger.ms': 60,
            'queue.buffering.max.messages': 5000000,
            'compression.type': 'lz4',
            'batch.num.messages': 50000,
            'batch.size': 200000,
            'logger': logger,
            'acks': 0 ,
            'error_cb': partial(self.error_callback),
        }
        return config


    def produce_to_topic(self,message):
        try:
            producer_conf = self.producer_config()
            producer = Producer(producer_conf)
            producer.produce(self.topic , value=json.dumps(message),on_delivery=partial(self.delivery_report))
            producer.poll()
            producer.flush()
            
        except ProduceError as e:
            logger.error(f"Failed to produce to topic '{self.topic}': {e}")
