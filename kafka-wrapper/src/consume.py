from kafka import KafkaConsumer, consumer
from flask import Flask, jsonify
import json
from kafka.consumer.fetcher import ConsumerRecord
import base64
class MessageConsumer:
    broker = ""
    topic = ""
    group_id = ""
    logger = None

    def __init__(self, broker, topic, group_id,count):
        self.broker = broker
        self.topic = topic
        self.group_id = group_id
        self.count = count
    def activate_listener(self):
        consumer = KafkaConsumer(bootstrap_servers=self.broker,
                                 group_id='my-group',
                                 consumer_timeout_ms=60000,
                                 auto_offset_reset='earliest',
                                 enable_auto_commit=False)
                                 

        consumer.subscribe(self.topic)
        print("consumer is listening....")
        result_array = []
        key = ''
        value = ''
        topic = ''
        partition = ''
        offset= ''
        consumed_messages = 0
        total_messages = self.count  # Define the total number of messages to consume 
        try:
            while consumed_messages < total_messages:
                for message in consumer:
                    if isinstance(message, ConsumerRecord):
                        print("received message = ", message)
                        print(message.key)
                        key = message.key.decode('utf-8') if message.key is not None else None
                        value = message.value.decode('unicode-escape') if message.value is not None else None
                        headers = message.headers if message.headers is not None else None
                        my_tuble=[]
                        print("head")
                        for each in headers:
                            print(type(each))
                            if isinstance(each,tuple):
                                test=[]
                                for each1 in each:
                                    if isinstance(each1,bytes):
                                        each1 = each1.decode("utf-8")  # Convert bytes to string
                                    test.append(each1)
                            my_tuble.append(test)
                        topic = message.topic
                        partition = message.partition
                        offset = message.offset
                        serializable_data = []
                        final=[]

                        for item in headers:
                            # Check if the item is serializable
                            try:
                                serialized_item = jsonify(item)
                                final.append(serialized_item)
                            except TypeError:
                                # Handle non-serializable item (e.g., set)
                                pass
                        #committing message manually after reading from the topic
                        consumer.commit()
                        response_data = {
                            'key': key,
                            'value': value,
                            'headers': final,
                            'topic': topic,
                            'partition': partition,
                            'offset': offset
                        }
                        response_data = json.dumps(response_data)
                        print(type(response_data))
                        existing_data = json.loads(response_data)
                        existing_data['headers'] = my_tuble
                        result_array.append(existing_data)
                        # print(result_array)
                        consumed_messages += 1
                        if consumed_messages >= total_messages:
                            break
                    else:
                        print("Received a different object type.")
                        # Handle other object types
        except KeyboardInterrupt:
            print("Aborted by user...")
        finally:
            consumer.close()

        
        # #Return the dictionary as JSON response
        # result_array=list(result_array)
        # for dictionary in result_array:
        #     for key, value in dictionary.items():
        #         if type(value) is list:
        #             for find in value:
        #                 print(type(find))
        #                 if isinstance(find, tuple):
        #                     for item in find:
        #                         print("inside end")
        #                         if isinstance(item, bytes):
        #                             print(item)
        #                             result_array[dictionary][key][value][find][item]=result_array base64.b64encode(item).decode()
        #                     # json_data = json.dumps(find)
        #                     # find1=json_data
        #                     # print(find1)
                            
        #                 # for key1, value1 in find.items():
        #                 #     print ("inside inside")
        #         if isinstance(value, bytes):
        #             dictionary[key] = value.decode('utf-8')  # Convert bytes to string
                
        # for element in json_data:
        #     print(type(element))
        # val=str(result_array)
        # json_object = json.loads(val)
        return jsonify(result_array)

