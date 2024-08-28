import logging
from functools import partial
import threading
import time
import requests
from confluent_kafka import OFFSET_END,Consumer,KafkaError,TopicPartition
from confluent_kafka.error import ConsumeError
import datetime
from logger_config import logger
from pm_metrics import consume_message
class MessageConsumeStartup:

    def __init__(self, broker, topic,count,iam_url,client_id,client_psw,group,broker_type):
        self.broker = broker
        self.topic = topic
        self.count = count
        self.iam_url = iam_url
        self.client_id = client_id
        self.client_psw = client_psw
        self.group = group
        self.broker_type = broker_type
    def error_callback(self,err):
        logger.error(f"Failed to connect kafka - {self.broker} - {err}")


            
    def _get_token(self,oauth_config):
        payload = {
            'grant_type': 'client_credentials'
        }
        resp = requests.post(self.iam_url, verify="/var/tmp/serverca.crt",
                            auth=(self.client_id, self.client_psw),
                            data=payload)
        token = resp.json()
        logger.info(f"access token refereshed for consumer:: {token['access_token']}")
        return token['access_token'], time.time() + float(token['expires_in'])

    def consumer_config(self,group):
        logger = logging.getLogger(__name__)
        config = {
            'group.id': group,
            'bootstrap.servers': self.broker ,
            'auto.offset.reset': 'earliest',
            'enable.auto.offset.store' : True,
            'error_cb': self.error_callback ,
        }
        if self.broker_type == "oauth":
            config.update({
                'security.protocol': 'sasl_ssl',
                'sasl.mechanisms': 'OAUTHBEARER',
                'oauth_cb': partial(self._get_token),
                'sasl.oauthbearer.config': 'oauth_cb',
                'security.protocol': 'SASL_SSL',
                'ssl.ca.location': '/var/tmp/serverca.crt',
            })
        return config
    
    def consume_from_topic(self,topic,group):
        consumer_conf = self.consumer_config(group)
        logger.info(f"Consumer configuration : {consumer_conf}")
        c = Consumer(consumer_conf)
        c.subscribe([topic])
        logger.info("Subscribing to topic")
        consumed_messages=0
        total_messages=self.count
        start =datetime.datetime.now()
        logger.info(f"started consuimg the records from '{topic}' at: date and time = %s" % start)
        while consumed_messages < total_messages:
            msgs = c.consume(1,timeout=1)
            #start=datetime.datetime.now()
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
                consume_message.labels(topic=topic).inc(len(msgs))
                if consumed_messages >= total_messages:
                    end =  datetime.datetime.now()
                    logger.info(f"Stopped consuming the records from '{topic}' at: date and time = %s" % end)               
                    c.close()
                    break
        difference = (end - start).total_seconds() * 1000
        logger.info(f"difference for '{topic}'  = %s" % difference)
    
    def secquence(self):
        # Create threads to produce messages for each topic in parallel
        processes = []
        logger.info(f"IAM url : {self.iam_url}")
        logger.info(f"Client ID : {self.client_id}")
        logger.info(f"Client Password : {self.client_psw}")
        logger.info(f"List of the topics for consume : {str(self.topic)}")
        logger.info(f"List of the consumer group : {str(self.group)}")
        for i in range(len(self.topic)):
            p = threading.Thread(target=self.consume_from_topic, args=(self.topic[i],self.group[i],))
            p.daemon = True
            processes.append(p)
            p.start()
        return("Consumer thread started")
