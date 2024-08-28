import logging
from confluent_kafka import Consumer,KafkaError
from logger_config import logger
import configuration
import json
from acmr_produce import AcmrProducer
import uuid
import time
from healthcheck import healthCheck
class AcmrConsumerStartUp:

    def __init__(self, broker,group,startup=False):
        self.broker = broker
        self.group = group
        self.startup = startup
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
        if (self.startup):
            healthCheck()
        
        consumer_conf = self.consumer_config(self.group)
        c = Consumer(consumer_conf)
        c.subscribe([configuration.acmr_topic])
        logger.info(f"Subscribing to {configuration.acmr_topic} :: consumer group {self.group}")
        messageuid = str(uuid.uuid4())
        compositionuid = str(uuid.uuid4())
        while True:
            msgs = c.poll()
            if msgs is None:
                continue
            if msgs.error():
                if msgs.error().code() == KafkaError._PARTITION_EOF:
                    logger.warn('End of partition reached')
                else:
                    logger.error('Error: {}'.format(msgs.error().str()))
            else:
                value = json.loads(msgs.value().decode('utf-8'))
                try:
                    if value["messageType"] == "PARTICIPANT_REGISTER":
                        if value["participantId"] == "101c62b3-8918-41b9-a747-d21eb79c6c99":
                            logger.info(f"new participant request :: {value}")
                            messageId = value["messageId"]
                            participantAcks = {
                                            "responseTo": messageId,
                                            "result": True,
                                            "message": "Participant Register Ack",
                                            "messageType": "PARTICIPANT_REGISTER_ACK",
                                            "participantId": "101c62b3-8918-41b9-a747-d21eb79c6c99"
                                        }
                            primeRequest =  {
                                    "participantDefinitionUpdates": [
                                        {
                                            "participantId": "101c62b3-8918-41b9-a747-d21eb79c6c99",
                                            "automationCompositionElementDefinitionList": [
                                                {
                                                    "acElementDefinitionId": {
                                                        "name": "com.ericsson.oss.app.mgr.ac.element.DataManagementAutomationCompositionElement",
                                                        "version": "1.0.0"
                                                    },
                                                    "automationCompositionElementToscaNodeTemplate": {
                                                        "type": "org.onap.policy.clamp.acm.DataManagementAutomationCompositionElement",
                                                        "type_version": "1.0.0",
                                                        "properties": {
                                                            "provider": "Ericsson",
                                                            "startPhase": 0,
                                                            "uninitializedToPassiveTimeout": 300,
                                                            "podStatusCheckInterval": 30
                                                        },
                                                        "name": "com.ericsson.oss.app.mgr.ac.element.DataManagementAutomationCompositionElement",
                                                        "version": "1.0.0",
                                                        "metadata": {},
                                                        "description": "The Automation Composition element for the rApp's Data Management component"
                                                    },
                                                    "outProperties": {}
                                                }
                                            ]
                                        }
                                    ],
                                    "messageType": "PARTICIPANT_PRIME",
                                    "messageId": "52e52841-5a61-40b1-82de-7128203fa8ef",
                                    "timestamp": "2024-05-30T14:49:28.406670526Z",
                                    "compositionId": "eae47634-df4f-4c47-9810-f53806287f88"
                                }
                            produ = AcmrProducer(configuration.broker,1)
                            produ.produce_to_topic(participantAcks,"Participant Acks")
                            time.sleep(5)
                            produ.produce_to_topic(primeRequest,"prime")
                            
                    if value["messageType"] == "PARTICIPANT_PRIME_ACK":
                        if value["participantId"] == "101c62b3-8918-41b9-a747-d21eb79c6c99":
                            logger.info(f"acks for primed request :: {value}")
                except KeyError as e:
                    logger.error(f"KeyError: {e} key not found in the value dictionary.") 
                except Exception as e:
                    logger.error(f"An unexpected error occurred: {e}") 
                        