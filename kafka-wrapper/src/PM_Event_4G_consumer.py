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
import os
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO)
class Avro4GMessageConsumer:
    broker = ""
    topic = ""
    group_id = ""
    logger = logging.getLogger(__name__)
    
    def __init__(self, broker, topic, group_id,count):
        self.broker = broker
        self.topic = topic
        self.group_id = group_id
        self.count = count
        self.FailCount = 0
        self.PassCount = 0
        self.FailedID =[]
        self.SR = 0
    '''
    
    
    '''    
    def get_schema(self,eventId,dataVersion):
        try:
            schema_content = ''
            file_path="/resources/4G_PM_Events/" + dataVersion + "/" + eventId + "/"
            files = os.listdir(file_path)
            with open(file_path + files[0], 'r') as avro_file:
                    # Parse the Avro schema
                schema_content = avro_file.read() 
            schema_content =  avro.schema.parse(schema_content)       
            return schema_content
        except Exception as e:
            self.logger.error(f"Failed to get schema from static folder  - {file_path} - {str(e)}")
    def deserialize_messgae(self,avro_value,schema,eventId):
        # Create a BinaryDecoder to read the avro_value as binary data
        value_reader = avro.io.BinaryDecoder(io.BytesIO(avro_value))
        # Create a DatumReader for reading data using the provided schema
        reader = avro.io.DatumReader(schema)
        try:
            # Deserialize the Avro value using the provided schema
            deserialized_value = reader.read(value_reader)
            # Increment the successful deserialization count
            self.PassCount += 1
            # Return the deserialized value
            return deserialized_value
        except Exception as e:
            # If an exception occurs during deserialization
            # Increment the failed deserialization count
            self.FailCount += 1
            # Add the schemaID to the list of failed IDs for tracking
            self.FailedID.append(eventId)
            # Log an error message indicating the failure
            self.logger.error(f"Failed to deserialized message for EventId - {eventId} - {str(e)}")
    def activate_listener(self):
        # Define the Kafka configuration
        conf = {
            'bootstrap.servers': self.broker,  # Replace with your Kafka broker(s)
            'group.id': self.group_id,       # Consumer group ID
            'auto.offset.reset': 'earliest'       # Start consuming from the beginning of the topic
        }
        # Create a Kafka consumer instance
        consumer = Consumer(conf)
        # Subscribe to a topic
        consumer.subscribe([self.topic])  # Replace 'my-topic' with your desired topic
        print("consumer is listening....")
        result_array = []
        key = ''
        value = ''
        topic = ''
        partition = ''
        offset= ''
        eventId=''
        dataVersion=''
        consumed_messages = 0
        total_messages = self.count  # Define the total number of messages to consume 
        start =datetime.datetime.now()
        try:
            while consumed_messages < total_messages:
                msg = consumer.poll(1.0)  # Poll for new messages, timeout in seconds
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print('End of partition reached')
                    else:
                        print('Error: {}'.format(msg.error().str()))
                else:
                    # key = msg.key().decode('utf-16') if msg.key() is not None else None
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
                        if my_tub[0] == 'eventId':  # Replace 'your_header_name' with the actual header name
                            eventId = my_tub[1]
                        elif my_tub[0] == 'dataVersion':
                            dataVersion = my_tub[1]      
                    schema = self.get_schema(eventId,dataVersion)
                    avro_value = msg.value()[5:]
                    deserialized_value = self.deserialize_messgae(avro_value,schema,eventId)
                    consumed_messages += 1
                    if consumed_messages >= total_messages:
                        end =  datetime.datetime.now()
                        break
            difference = end - start
            self.logger.info("difference = %s" % difference)
            UniqueFailedID = set(self.FailedID)
            UniqueFailedID = list(UniqueFailedID)
            response_dat = {
                'deserialization-passed': self.PassCount,
                'deserialization-failed': self.FailCount,
                'deserizlization-FailedEventid': UniqueFailedID
             }
            self.logger.warning(f"List of failed deserialization EventID - {UniqueFailedID}")
            return json.dumps(response_dat)
        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()