import requests
import logging
import json
import config
from messagebus import datacatalog 
from PM_consume import PmMessageConsumeOauth
from Event_4G_consume import PMEvent4GMessageConsumeOauth
import time
from unpackage import unpack
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO)
class start_listener:
    logger = logging.getLogger(__name__)
   
    def start_consumer(self):
        listener = datacatalog(config.userName,config.userPassword,config.gas_uri)
        while True:
            test=listener.subscription()
            if (test != 0):
                topicName= listener.subscription_notificationTopic()
                self.logger.info(f"Topic name from data catalog - {topicName}")
                external_host = listener.external_broker()
                self.logger.info(f"Kafka external host from data catalog  - {external_host}")
                if "ran" in topicName:  
                    consumer = PmMessageConsumeOauth(external_host,topicName,config.iam_uri,config.client_id,config.client_psw,"consumer-group")
                    consumer.start_kafka_consumer()
                elif "ctr-processed" in topicName:
                    untar = unpack("4G_PM_Events_242_23_Q4.tgz")
                    untar.untar_file()
                    consumer = PMEvent4GMessageConsumeOauth(external_host,topicName,config.iam_uri,config.client_id,config.client_psw,"consumer-group")
                    consumer.start_kafka_consumer()
                break
            self.logger.info("Waiting for subscription")
            time.sleep(20)