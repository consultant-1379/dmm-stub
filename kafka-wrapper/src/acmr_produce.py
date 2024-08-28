from functools import partial
from confluent_kafka import Producer
from confluent_kafka.error import ProduceError
from logger_config import logger
import json
import configuration
class AcmrProducer:

    def __init__(self, broker,count):
        self.broker = broker
        self.count = count
    def error_callback(self,err):
        logger.error(f" Failed to connect kafka - {self.broker} - {err}")
        raise err


    def delivery_report(self, err, msg,operation):
        if err:
            raise Exception(f" Delivery failed for Produce record at  {msg.key()}: {err}")
        else:
            logger.info(f"{operation} request sent sucessfully :: {msg}")
            
    def producer_config(self):
        config = {
            'bootstrap.servers': self.broker,
            'linger.ms': 60,
            'queue.buffering.max.messages': 5000000,
            'compression.type': 'lz4',
            'batch.num.messages': 50000,
            'batch.size': 200000,
            'logger': logger,
            'acks': -1 ,
            'error_cb': partial(self.error_callback),
        }
        return config


    def produce_to_topic(self,message,opr,automationCompositionIds=None,acElementListIds=None,rAppIds=None):
        try:
            producer_conf = self.producer_config()
            producer = Producer(producer_conf)
            for x in range(0,self.count):
                if opr =="Deploy" or opr == "UNDeploy":
                    message["automationCompositionId"]=automationCompositionIds[x]
                    if opr == "Deploy":
                        message["participantUpdatesList"][0]["acElementList"][0]["id"]=acElementListIds[x]
                        message["participantUpdatesList"][0]["acElementList"][0]["properties"]["iamClientId"]=rAppIds[x]
                producer.produce(configuration.acmr_topic , value=json.dumps(message),on_delivery=partial(self.delivery_report, operation=opr))
            producer.poll()
            producer.flush()
            
        except ProduceError as e:
            logger.error(f"Failed to produce to topic '{configuration.acmr_topic}': {e}")
