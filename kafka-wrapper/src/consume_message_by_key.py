from confluent_kafka.avro import AvroConsumer
from confluent_kafka import Consumer
from flask import abort
import requests
import avro.schema
import avro.io
import io
import datetime
import json
import functools
import logging
from PM_Counter_consumer import AvroRanMessageConsumer

#desired_key="SubNetwork=Europe,SubNetwork=Ireland,MeContext=NR02gNodeBRadio00912,ManagedElement=NR02gNodeBRadio00912"
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO)

class AvroRanMessageConsumer_static(AvroRanMessageConsumer):
    broker = ""
    topic = ""
    group_id = ""
    logger = logging.getLogger(__name__)
    
    
    def __init__(self, broker, topic, group_id):
        self.broker = broker
        self.topic = topic
        self.group_id = group_id
        self.FailCount = 0
        self.PassCount = 0
        self.SR = 0
    '''
    
    
    '''    
    
    def activate_listeners(self,desired_key):
        # Define the Kafka configuration
        conf = {
            'bootstrap.servers': self.broker,  # Replace with your Kafka broker(s)
            'group.id': self.group_id,       # Consumer group ID
            'auto.offset.reset': 'latest'        # Start consuming from the beginning of the topic
        }

        # Create a Kafka consumer instance
        consumer = Consumer(conf)

        # Subscribe to a topic
        consumer.subscribe([self.topic])  # Replace 'my-topic' with your desired topic
        print("consumer is listening....")
        key = ''
        schemaID=''
        consumed_messages = 0
        total_messages = 1  
        try:
            while consumed_messages < total_messages:
                msg = consumer.poll(1.0)  # Poll for new messages, timeout in seconds
                #print("polling....")
                if msg is None:
                    #print("checking for message no message")
                    continue
                    
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print('End of partition reached')
                    else:
                        print('Error: {}'.format(msg.error().str()))
                else:
                    key = msg.key().decode('utf-8') if msg.key() is not None else None
                    if key==desired_key:
                        my_tuble=[]
                        for each in msg.headers():
                            if isinstance(each,tuple):
                                test=[]
                                for each1 in each:
                                    if isinstance(each1,bytes):
                                        each1 = each1.decode("utf-8")  # Convert bytes to string
                                    test.append(each1)
                            my_tuble.append(test)
                        for my_tub in my_tuble:
                            if my_tub[0] == 'schemaID':  # Replace 'your_header_name' with the actual header name
                                schemaID = my_tub[1]
                                break             
                        schema = self.get_schema(schemaID)
                        avro_value = msg.value()[5:]
                        deserialized_value = self.deserialize_messgae(avro_value,schema,schemaID)                    
                        #print("Deserialised Values : ",deserialized_value)
                        consumed_messages += 1
                        return deserialized_value
                    
                    

        except KeyboardInterrupt:
            pass

        finally:
            consumer.close()


