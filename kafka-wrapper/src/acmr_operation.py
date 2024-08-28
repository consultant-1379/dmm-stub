import logging
from confluent_kafka import Consumer,KafkaError
from logger_config import logger
import configuration
import json
from acmr_produce import AcmrProducer
import uuid
import time
import threading

class AcmrOperation:

    def __init__(self, broker,group,msg,count,automationCompositionIds,acElementListIds=None,rAppIds=None):
        self.broker = broker
        self.group = group
        self.msg = msg
        self.count =count
        self.automationCompositionIds = automationCompositionIds
        self.acElementListIds = acElementListIds
        self.rAppIds = rAppIds
    def error_callback(self,err):
        logger.error(f"Failed to connect kafka - {self.broker} - {err}")
        raise err

    def consumer_config(self,group):
        logger = logging.getLogger(__name__)
        config = {
            'group.id': group,
            'bootstrap.servers': self.broker ,
            'auto.offset.reset': 'latest',
            'error_cb': self.error_callback ,
        }
        return config
    def subtract_json_values(self,json1, json2):
        # Initialize the result JSON object
        result_json = {}

        # Iterate through the keys in the first JSON object
        for key in json1:
            if key in json2:
                result_json[key] = json1[key] - json2[key]

        return result_json    
    def consume_from_topic(self,result,req):
        consumer_conf = self.consumer_config(self.group)
        c = Consumer(consumer_conf)
        c.subscribe([configuration.acmr_topic])
        SucessCount= 0
        FailCount = 0
        logger.info(f"Subscribing to {configuration.acmr_topic} :: consumer group {self.group}")
        produceTime={}
        consumeTime={}
        failedbody={}
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
                if value["messageType"] == "AUTOMATION_COMPOSITION_DEPLOY":
                    if value["participantUpdatesList"][0]["participantId"] == "101c62b3-8918-41b9-a747-d21eb79c6c99":
                        if value["automationCompositionId"] in self.automationCompositionIds:
                            timestamp_type, timestamp = msgs.timestamp()
                            produceTime[value["automationCompositionId"]]=timestamp
                            
                if value["messageType"] == "AUTOMATION_COMPOSITION_STATE_CHANGE":
                    if value["automationCompositionId"] in self.automationCompositionIds:
                        timestamp_type, timestamp = msgs.timestamp()
                        produceTime[value["automationCompositionId"]]=timestamp
                            
                if value["messageType"] == "AUTOMATION_COMPOSITION_STATECHANGE_ACK":
                    if value["participantId"] == "101c62b3-8918-41b9-a747-d21eb79c6c99":
                        if value["automationCompositionId"] in self.automationCompositionIds:
                            timestamp_type, timestamp = msgs.timestamp()
                            consumeTime[value["automationCompositionId"]]=timestamp
                            if value["stateChangeResult"] == "FAILED":
                                FailCount += 1
                                failedbody[value["automationCompositionId"]]=value
                            if value["stateChangeResult"] == "NO_ERROR":
                                SucessCount +=1
                                # failedbody[value["automationCompositionId"]]=value
                            if self.count == SucessCount+FailCount:
                                c.close()
                                break
        # print( {"sucesscount":SucessCount,"failedcount":FailCount,"failed":failedbody})
        final= self.subtract_json_values(consumeTime,produceTime)
        result.append( {"sucesscount":SucessCount,"failedcount":FailCount,"failed":failedbody,"timetaken":final})
                            
                        
                        
               
  
  
    def start_deploy_thread(self):
        result=[]                    
        adctest_thread = threading.Thread(target=self.consume_from_topic,args=(result,"Deploy",))
        adctest_thread.start()
        time.sleep(10)
        test1 =AcmrProducer(configuration.broker,self.count)
        test1.produce_to_topic(self.msg,"Deploy",self.automationCompositionIds,self.acElementListIds,self.rAppIds)
        adctest_thread.join()
        return result

    def start_undeploy_thread(self):
        result=[]                    
        adctest_thread = threading.Thread(target=self.consume_from_topic,args=(result,"UNDeploy"))
        adctest_thread.start()
        time.sleep(10)
        test1 =AcmrProducer(configuration.broker,self.count)
        test1.produce_to_topic(self.msg,"UNDeploy",self.automationCompositionIds)
        adctest_thread.join()
        return result