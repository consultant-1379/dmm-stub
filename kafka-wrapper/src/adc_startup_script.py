import logging
from functools import partial
import threading
import time
import requests
from confluent_kafka import OFFSET_END,Consumer,KafkaError,TopicPartition
from confluent_kafka.error import ConsumeError
import datetime
from logger_config import logger
from configuration import broker,topicbuffertime,gettopicsfromenv
from pm_metrics import consume_message
adctopics = gettopicsfromenv()

def consumer_config():

    config = {
        'group.id': "adc",
        'bootstrap.servers': broker ,
        'auto.offset.reset': 'latest',
        'enable.auto.offset.store' : True,
    }
    return config

def consume_from_adctopics():

    while True:
        try:
            response = requests.get('http://127.0.0.1:8082/health')
            if response.status_code == 200:
                logger.info("Wrapper is ready")
                break
        except requests.ConnectionError:
            logger.error("Connection refused. Retrying in 5 seconds...")
            time.sleep(5)

    logger.info(f" Array topics from configuration method {adctopics}")
    actualtopics_kafka = []

    i = 0
    while i < topicbuffertime:
        for topic in adctopics:
            response = requests.get(f'http://127.0.0.1:8082/topic/{topic}')
            if 200 == response.status_code:
                if topic not in actualtopics_kafka:
                    actualtopics_kafka.append(topic)
        if len(actualtopics_kafka) == len(adctopics):
            break
        time.sleep(30)
        i += 30

    consumer_conf = consumer_config()
    logger.info(f"Consumer configuration : {consumer_conf}")
    c = Consumer(consumer_conf)
    c.subscribe(adctopics)
    logger.info("Subscribed to ADC topic")
    consumed_messages=0
    start =datetime.datetime.now()

    while True:
        msgs = c.consume(1,timeout=1)
        if msgs is None or len(msgs) == 0:
            logger.info("waiting for msg")
            continue
        if msgs:
            for msg in msgs:
                if msg.error():
                    # Handle Kafka errors
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug(f"Consumed all the messages")
                    else:
                        logger.debug(f"Error: {msg.error()}")
            consumed_messages += len(msgs)
            consume_message.labels(topic=msg.topic()).inc()



