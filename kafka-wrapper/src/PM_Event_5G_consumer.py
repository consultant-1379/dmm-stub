from confluent_kafka import Consumer
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
import json

 
# Imported after manually compiling using protoc and dropping pm_event folder into project
# Only need 3 middle layer network functions and the outer wrapper class in this instance
import pm_event.cu_cp_function_pm_event_pb2 as cucp_function_event
import pm_event.cu_up_function_pm_event_pb2 as cuup_function_event
import pm_event.du_function_pm_event_pb2 as du_function_event
import pm_event.pm_event_pb2 as pm_event_outer
import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO)
class Proto5GGMessageConsumer:
    broker = ""
    topic = ""
    group_id = ""
    logger = logging.getLogger(__name__)
    
    def __init__(self, broker, topic, group_id,count):
        self.broker = broker
        self.topic = topic
        self.group_id = group_id
        self.count = count
        self.OuterFailCount = 0
        self.OuterPassCount = 0
        self.FunctionalFailCount = 0
        self.FunctionalPassCount = 0
        self.cuup =0
        self.cucp =0
        self.du = 0
        self.InValidGroup = 0

    
    def functional_decode_messgae(self,inner_event,payload,event_id,message_group):
        try:
            inner_event.ParseFromString(payload)
            self.FunctionalPassCount += 1
        except Exception as e:
            self.logger.error(f"Failed to decode message for EventName - {inner_event.WhichOneof('event_payload')}, EventId - {event_id} ,Event group - {message_group}- {str(e)}")
            self.FunctionalFailCount +=1
    
    def decode_event(self, pm_event: pm_event_outer):
        event_id = pm_event.event_id
        message_group = pm_event.group
        payload = pm_event.payload
        if message_group == pm_event_outer.PM_EVENT_MESSAGE_GROUP_NO_VALUE:
            self.logger.error(f"Invalid message group found in outer message - {message_group}")
            self.InValidGroup += 1
        elif message_group == pm_event_outer.PM_EVENT_MESSAGE_GROUP_CUUP:
            self.cuup += 1
            cuup_event = cuup_function_event.CuUpFunctionPmEvent()
            self.functional_decode_messgae(cuup_event,payload,event_id,message_group)
        elif message_group == pm_event_outer.PM_EVENT_MESSAGE_GROUP_CUCP:
            self.cucp += 1
            cucp_event = cucp_function_event.CuCpFunctionPmEvent()
            self.functional_decode_messgae(cucp_event,payload,event_id,message_group)
        elif message_group == pm_event_outer.PM_EVENT_MESSAGE_GROUP_DU:
            self.du += 1
            du_event = du_function_event.DuFunctionPmEvent()
            self.functional_decode_messgae(du_event,payload,event_id,message_group)
    
    def outer_decode_message(self,msg):
        try:
            protobuf_deserializer = ProtobufDeserializer(pm_event_outer.PmEvent, {'use.deprecated.format': False})
            pm_event_outer_wrapper = protobuf_deserializer(msg, SerializationContext(
                        topic=self.topic, field=MessageField.VALUE))
            self.OuterPassCount +=1
            return pm_event_outer_wrapper
        except Exception as e:
            self.logger.error(f"Failed to decode outer message -  {str(e)}")
            self.OuterFailCount +=1
    def start_consuming(self):
        consumed_messages = 0
        total_messages = self.count  # Define the total number of messages to consume 
    # Create a Consumer instance
        consumer_conf = {'bootstrap.servers': self.broker,
                        'group.id': 'my-group',
                        'auto.offset.reset': "earliest"}
        consumer = Consumer(consumer_conf)
    
        # Subscribe to the topic
        consumer.subscribe([self.topic])
    
        while consumed_messages < total_messages:
            # Poll for messages
            msg = consumer.poll(1.0)
            if msg is None:
                print("No messages yet..")
                continue
    
            # Check if the message was received successfully
            if msg.error():
                print("Error consuming message:", msg.error())
                continue
            else:
                outer_message=self.outer_decode_message(msg.value())
                self.decode_event(outer_message)
                consumed_messages += 1
                if consumed_messages >= total_messages:
                    break
        response_dat = {
            'decode-outer-passed': self.FunctionalPassCount,
            'decode-outer-failed': self.FunctionalFailCount,
            'decode-functional-passed': self.OuterPassCount,
            'decode-functional-failed': self.OuterFailCount,
            'cucp-group-count': self.cucp,
            'cuup-group-count': self.cuup,
            'du-group-count': self.du,
            'invalid-message-group-count': self.InValidGroup
         }
        return json.dumps(response_dat)

    
 

    
    
    
    
    