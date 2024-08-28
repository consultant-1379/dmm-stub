import requests
import configuration
import threading
import time
from produce_startup import MessageProduceStartup
from consume_startup import MessageConsumeStartup
from random_string import create_string_from_bytes
import uuid
from data_catalog import DataCatalog
from logger_config import logger
import numpy as np
def start_kafka_client():
    while True:
        try:
            response = requests.get('http://127.0.0.1:8082/health')
            if response.status_code == 200:
                logger.info("Wrapper is ready")
                break
        except requests.ConnectionError:
            logger.error("Connection refused. Retrying in 5 seconds...")
            time.sleep(5)
    TopicName = np.array([
        f"dmm-app-eng-{uuid.uuid4()}",
        f"dmm-app-eng-{uuid.uuid4()}",
        f"dmm-app-eng-{uuid.uuid4()}",
        f"dmm-app-eng-{uuid.uuid4()}"
    ])

    # Converting numpy array to a Python list
    TopicName = TopicName.tolist()
    logger.info(f"Produce Topic Name - {TopicName}")
    logger.info(f"Total msg going to process - {configuration.count}")
    logger.info(f"Each replica  going to process - {configuration.messageCount_topic}")
    logger.info(f"Size of the messages - {configuration.size}")
    data = {
              "partitions": 30, 
              "replicas": 3,
              "topics": TopicName
            }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post('http://127.0.0.1:8082/topic', json=data,headers=headers)
    if response.status_code == 200:
        logger.info(f'Topic is Created sucessfully :: {TopicName} :: {response.status_code} :: {response.text}')
    else:
        logger.error(f'Topic is Creation got failed :: {TopicName} :: {response.status_code} :: {response.text}')
    message =create_string_from_bytes(configuration.size)
    logger.info(f"Generated message :: {message}")
    
    # Creating file format
    fileFormat = DataCatalog()
    fileFormat.register_fileformat()
    fileFormat.retrive_subscription()
    
    topic = TopicName
    broker = configuration.external_broker
    iam_url = configuration.iam_uri
    count = configuration.messageCount_topic
    broker_type = "oauth"
    producer = MessageProduceStartup(broker,topic,count,iam_url,configuration.client_id,configuration.client_psw,message,broker_type)
    pro = producer.secquence()
# COnsumer 
    logger.info(f"Muliprocessing")
    group =f"dmm-app-eng-{uuid.uuid4()}"
    logger.info(f"consumer Group Name :: {group}")
    topic = TopicName
    broker = configuration.external_broker
    iam_url = configuration.iam_uri
    count = configuration.messageCount_topic
    broker_type = "oauth"
    consumer = MessageConsumeStartup(broker,topic,count,iam_url,configuration.client_id,configuration.client_psw,group,broker_type)
    con = consumer.secquence()