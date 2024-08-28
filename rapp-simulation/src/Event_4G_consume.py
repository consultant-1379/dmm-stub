import logging
from functools import partial
import threading
import argparse
import time
from uuid import uuid4
import requests
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka import OFFSET_END,Consumer,KafkaError,TopicPartition
import datetime
import sys
import functools
import avro.schema
import avro.io
import io
from metrics import pm_event_4g_consume_sucess_counter,pm_event_4g_consume_failure_counter
from config import platformcaCertFileFullPath ,kafkacaCertFileFullPath , gas_uri
import os
class PMEvent4GMessageConsumeOauth:
    logger = logging.getLogger(__name__)

    def __init__(self, broker, topic,iam_url,client_id,client_psw,group):
        self.broker = broker
        self.topic = topic
        self.iam_url = iam_url
        self.client_id = client_id
        self.client_psw = client_psw
        self.group = group
        self.FailCount = 0
        self.PassCount = 0
        self.FailedID =[]
        self.SR = 0
    def error_callback(self,err):
        print("callback hit!")
        raise(err)


            
    def _get_token(self,oauth_config):
        payload = {
            'grant_type': 'client_credentials'
        }
        resp = requests.post(self.iam_url, verify=platformcaCertFileFullPath,
                            auth=(self.client_id, self.client_psw),
                            data=payload)
        token = resp.json()
        self.logger.info(f"Oauth token is refreshed for client - {self.client_id}")
        return token['access_token'], time.time() + float(token['expires_in'])


    def get_schema(self,eventId,dataVersion):
        try:
            schema_content = ''
            file_path="/resources/4G_PM_Events/" + dataVersion + "/" + eventId + "/"
            files = os.listdir(file_path)
            with open(file_path + files[0], 'r') as avro_file:
                    # Parse the Avro schema
                schema_content = avro_file.read() 
        except FileNotFoundError as e:
            self.logger.error(f"Failed to get schema from static folder  - {file_path} - {str(e)}")
        else:
            schema_content =  avro.schema.parse(schema_content)       
            return schema_content         
            
    def deserialize_message(self,avro_value,schema,eventId):
        # Create a BinaryDecoder to read the avro_value as binary data
        value_reader = avro.io.BinaryDecoder(io.BytesIO(avro_value))
        # Create a DatumReader for reading data using the provided schema
        reader = avro.io.DatumReader(schema)
        try:
            # Deserialize the Avro value using the provided schema
            deserialized_value = reader.read(value_reader)
            # Increment the successful deserialization count
            self.PassCount += 1
            pm_event_4g_consume_sucess_counter.inc()
            # Return the deserialized value
            return deserialized_value
        except Exception as e:
            # If an exception occurs during deserialization
            # Increment the failed deserialization count
            self.FailCount += 1
            pm_event_4g_consume_failure_counter.inc()
            # Add the schemaID to the list of failed IDs for tracking
            self.FailedID.append(eventId)
            # Log an error message indicating the failure
            self.logger.error(f"Failed to deserialized message for EventId - {eventId} - {str(e)}")

    def consumer_config(self):
        logger = logging.getLogger(__name__)
        config = {
            'group.id': self.group,
            'bootstrap.servers': self.broker ,
            'auto.offset.reset': 'earliest',
            'error_cb': self.error_callback ,
            'security.protocol': 'sasl_ssl',
            'sasl.mechanisms': 'OAUTHBEARER',
            'oauth_cb': partial(self._get_token),
            'sasl.oauthbearer.config': 'oauth_cb',
            'security.protocol': 'SASL_SSL',
            'ssl.ca.location': kafkacaCertFileFullPath,
        }
        return config
    
    def consume_from_topic(self):
        consumer_conf = self.consumer_config()
        self.logger.info(f"Consumer config {consumer_conf}")
        c = Consumer(consumer_conf)
        c.subscribe([self.topic])
        self.logger.info(f"Subscribed to topic {self.topic}")
        start =datetime.datetime.now()
        count = 0
        self.logger.info(f"started consuming the records from '{self.topic}' at: date and time = %s" % start)
        while True:
            msg = c.poll(1.0)  # Poll for new messages, timeout in seconds
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    self.logger.error('End of partition reached')
                else:
                    self.logger.error('Error: {}'.format(msg.error().str()))
            else:
                # key = msg.key().decode('utf-8') if msg.key() is not None else None
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
                deserialized_value = self.deserialize_message(avro_value,schema,eventId)
                count += 1
                # print(count)
                # print(deserialized_value)
                # break



    def start_kafka_consumer(self):
        consumer_thread = threading.Thread(target=self.consume_from_topic)
        consumer_thread.daemon = True
        consumer_thread.start()

    