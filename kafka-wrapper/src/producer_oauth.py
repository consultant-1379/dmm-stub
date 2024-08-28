
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
class MessageProduceOauth:

    def __init__(self, broker, topic,count,iam_url,client_id,client_psw,message,broker_type):
        self.broker = broker
        self.topic = topic
        self.count = count
        self.iam_url = iam_url
        self.client_id = client_id
        self.client_psw = client_psw
        self.message = message
        self.broker_type = broker_type
        self.exception_queue = Queue()
    def error_callback(self,err,threadID):
        logger.error(f"Thread : {threadID} : Failed to connect kafka - {self.broker} - {err}")
        raise err


    def _get_token(self,oauth_config):
        payload = {
            'grant_type': 'client_credentials'
        }
        resp = requests.post(self.iam_url, verify="/var/tmp/serverca.crt",
                            auth=(self.client_id, self.client_psw),
                            data=payload)
        token = resp.json()
        return token['access_token'], time.time() + float(token['expires_in'])

    def delivery_report(self, err, msg,threadID):
        if err:
            raise Exception(f"Thread : {threadID} : Delivery failed for Produce record at  {msg.key()}: {err}")
            
    def producer_config(self,threadID):
        config = {
            'bootstrap.servers': self.broker,
            'linger.ms': 60,
            'queue.buffering.max.messages': 5000000,
            'compression.type': 'lz4',
            'batch.num.messages': 50000,
            'batch.size': 200000,
            'logger': logger,
            'acks': 0 ,
            'error_cb': partial(self.error_callback, threadID=threadID),
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


    def produce_to_topic(self,topic,results):
        threadID = threading.get_ident()
        try:
            start =datetime.datetime.now()
            logger.info(f"Thread : {threadID} : Started producing the records for '{topic}' at: date and time = %s" % start)
            producer_conf = self.producer_config(threadID)
            logger.info(f"Thread : {threadID} : Producer configuration : {producer_conf}")
            producer = Producer(producer_conf)
            for x in range(0,self.count):
                producer.produce(topic ,key=f"message count {self.count}", value=self.message,on_delivery=partial(self.delivery_report, threadID=threadID))
            end =  datetime.datetime.now()
            producer.poll()
            producer.flush()
            logger.info(f"Thread : {threadID} : Stopped producing the records for '{topic}' at: date and time = %s" % end)
            difference = (end - start).total_seconds() * 1000
            logger.info(f"Thread : {threadID} : difference for '{topic}'  = %s" % difference)

            results.append(difference)
            
        except ProduceError as e:
            logger.error(f"Thread : {threadID} : Failed to produce to topic '{topic}': {e}")

    def secquence(self):
        # Create threads to produce messages for each topic in parallel
        logger.info(f"IAM url : {self.iam_url}")
        logger.info(f"Client ID : {self.client_id}")
        logger.info(f"Client Password : {self.client_psw}")
        threads = []
        results = []
        logger.info(f"total topic : {str(len(self.topic))}")
        for i in range(len(self.topic)):
            t = threading.Thread(target=self.produce_to_topic, args=(self.topic[i],results,))
            threads.append(t)
            t.start()

        # Wait for all threads to finish
        for t in threads:
            t.join()

        print(f"All producer results :: {results}")
        # Calculate the total sum of values from all threads
        percentile = np.percentile(results , 98)
        result={
                "status": f"sucessfully produced {str(self.count)} messages across {str(len(self.topic))} topics",
                "timetaken": percentile
        }
        return result