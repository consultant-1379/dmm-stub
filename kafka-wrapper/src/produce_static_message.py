from confluent_kafka import Producer
import json,logging
from confluent_kafka.error import ProduceError
from logger_config import logger

 
# Kafka broker settings
headers = {"nodeName":"SubNetwork=Europe,SubNetwork=Ireland,MeContext=NR02gNodeBRadio00912,ManagedElement=NR02gNodeBRadio00912","spring_json_header_types":"{\"nodeName\":\"java.lang.String\",\"subSystemType\":\"java.lang.String\",\"dataType\":\"java.lang.String\",\"nodeType\":\"java.lang.String\"}","subSystemType":"pENM","dataType":"PM_STATISTICAL","nodeType":"RadioNode","__TypeId__":"java.lang.String"}  

# message_key = 'SubNetwork=Europe,SubNetwork=Ireland,MeContext=NR02gNodeBRadio00912,ManagedElement=NR02gNodeBRadio00912'  

# message = "{\"fileLocation\":\"ran-pm-counter-sftp-file-transfer/testfile.xml.gz\"}"
#message = '{"fileLocation":"ran-pm-counter-sftp-file-transfer/testfile.xml.gz"}'
class Static_Producer:
    broker = ""
    topic = ""
    logger = logging.getLogger(__name__)
    

    def __init__(self, broker, topic):
        self.broker = broker
        self.topic = topic
        
    delivery_status = {}
    def delivery_report(self,err,msg):
        if err is not None:
            self.logger.info(f"Delivery failed for Produce record at {self.topic}: {err}")
            self.delivery_status[msg.key()] = "Failed"
        else:
            #print(f"Delivery to {self.topic}")
            self.delivery_status[msg.key()] = "Delivered"
            
    def producer(self,message_key,message):
        conf = {
            'bootstrap.servers': self.broker
        }
        # Create Kafka producer
        try:
            producer = Producer(conf)
            producer.produce(self.topic,key=message_key, value=json.dumps(message),headers=headers, callback=self.delivery_report)  #json.dumps convert a subset of Python objects into a json string
            # Wait for message delivery
            producer.poll()
            status=self.delivery_status
            converted_dict = {key.decode(): value for key, value in status.items()}
            return converted_dict[message_key]
        except ProduceError as e:
            logger.error(f"Failed to produce to topic '{self.topic}': {e}")