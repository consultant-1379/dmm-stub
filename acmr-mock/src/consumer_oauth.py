import logging
from confluent_kafka import Consumer,KafkaError
from logger_config import logger
import configuration
import json
from producer_oauth import MessageProduceOauth
import uuid
import time

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
        c = Consumer(consumer_conf)
        c.subscribe([self.topic])
        logger.info("Subscribing to topic")
        messageuid = str(uuid.uuid4())
        compositionuid = str(uuid.uuid4())
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
                if value["messageType"] == "PARTICIPANT_REGISTER":
                    if value["participantId"] == "101c62b3-8918-41b9-a747-d21eb79c6c99":
                        logger.info(f"new participant request :: {value}")
                        messageId = value["messageId"]
                        message = {
                                        "responseTo": messageId,
                                        "result": True,
                                        "message": "Participant Register Ack",
                                        "messageType": "PARTICIPANT_REGISTER_ACK",
                                        "participantId": "101c62b3-8918-41b9-a747-d21eb79c6c99"
                                    }
                        message1 =  {
                            "participantDefinitionUpdates": [
                                {
                                    "participantId": "101c62b3-8918-41b9-a747-d21eb79c6c99",
                                    "automationCompositionElementDefinitionList": [
                                        {
                                            "acElementDefinitionId": {
                                                "name": "onap.policy.clamp.ac.element.DataSubscription_TestAutomationCompositionElement",
                                                "version": "1.2.3"
                                            },
                                            "automationCompositionElementToscaNodeTemplate": {
                                                "type": "org.onap.policy.clamp.acm.DataSubscriptionAutomationCompositionElement",
                                                "type_version": "1.0.0",
                                                "properties": {
                                                    "provider": "ONAP",
                                                    "uninitializedToPassiveTimeout": 300,
                                                    "startPhase": 0
                                                },
                                                "name": "onap.policy.clamp.ac.element.DataSubscription_TestAutomationCompositionElement",
                                                "version": "1.2.3",
                                                "metadata": {},
                                                "description": "Automation composition element for the Data Subscription requests"
                                            },
                                            "outProperties": {}
                                        }
                                    ]
                                }
                            ],
                            "messageType": "PARTICIPANT_PRIME",
                            "messageId": messageuid,
                            "timestamp": "2023-10-20T13:22:55.084583190Z",
                            "compositionId": "0c9af7cc-c543-437a-b603-cd8e00d021bb"
                        }
                        produ = MessageProduceOauth(configuration.broker,self.topic)
                        produ.produce_to_topic(message)
                        time.sleep(5)
                        produ.produce_to_topic(message1)
                        
                if value["messageType"] == "PARTICIPANT_PRIME_ACK":
                    if value["participantId"] == "101c62b3-8918-41b9-a747-d21eb79c6c99":
                        logger.info(f"acks for primed request :: {value}")
                        
                # if value["messageType"] == "AUTOMATION_COMPOSITION_STATECHANGE_ACK":
                #     if value["participantId"] == "101c62b3-8918-41b9-a747-d21eb79c6c99":
                #         logger.info(f"acks for deploy request :: {value}")
                #         print(msgs.timestamp())