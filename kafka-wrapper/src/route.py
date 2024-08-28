from time import sleep
import json
from flask import Flask,jsonify,abort,request
from consume import MessageConsumer
from topic import KafkaManager
from create_kafka_user import KafkaUser
from producer_oauth import MessageProduceOauth
from consumer_oauth import MessageConsumeOauth
from PM_Counter_consumer import AvroRanMessageConsumer
from PM_Event_4G_consumer import Avro4GMessageConsumer
from PM_Event_5G_consumer import Proto5GGMessageConsumer
import requests
import os
import logging
import configuration
from produce_startup import MessageProduceStartup
from consume_startup import MessageConsumeStartup
from acmr_operation import AcmrOperation
from prometheus_client import generate_latest
from prometheus_client import multiprocess
from prometheus_client import CollectorRegistry, CONTENT_TYPE_LATEST, Counter
from bdr import Upload_file_into_BDR ,Create_bucket
from produce_static_message import Static_Producer ,headers
from consume_message_by_key import AvroRanMessageConsumer_static
import uuid
from werkzeug.utils import secure_filename
import traceback

app = Flask(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO)

@app.route('/metrics')
def prometheus_metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return generate_latest(registry) 

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/topic/<topic>/<int:count>',methods=['GET'])
def test(topic,count):

    #Running multiple consumers
    broker = configuration.broker
    group_id = 'consumer-1'
    consumer1 = MessageConsumer(broker,topic,group_id,count)
    msg=consumer1.activate_listener()
    return msg

@app.route('/topic/<topic>',methods=['GET'])
def topic_check(topic):

    #Running multiple consumers
    broker = configuration.broker
    admin = KafkaManager(broker,topic)
    topics=admin.check_topic()
    return topics

@app.route('/topics',methods=['GET'])
def list_topic():

    #Running multiple consumers
    broker = configuration.broker
    admin = KafkaManager(broker)
    topics=admin.list_topics()
    return topics

@app.route('/topic/<topic>/describe',methods=['GET'])
def describe(topic):

    #Running multiple consumers
    broker = configuration.broker
    response = requests.get('http://127.0.0.1:8082/topic/'+topic)
    if response.status_code != 200:
        abort(400,"Topic is not available")

    admin = KafkaManager(broker,topic)
    describe=admin.describe_topic()
    return describe

@app.route('/topic',methods=['POST'])
def create_topic():
    payload = request.get_json()
    print(payload)
    Partitions =int(payload["partitions"])
    Replicas =int(payload["replicas"])
    topics =payload["topics"]
    print(Partitions)
    print(Replicas)
    print(topics)
    broker = configuration.broker
    admin = KafkaManager(broker,topics,Partitions,Replicas)
    topics=admin.create_topic()
    return topics

@app.route('/delete-topic',methods=['POST'])
def delete_topic():
    payload = request.get_json()
    print(payload)
    topics =payload["topics"]
    print(topics)
    broker = configuration.broker
    admin = KafkaManager(broker,topics)
    topics=admin.delete_topic()
    return topics
@app.route('/kafka-user/create-user',methods=['POST'])
def create_user():
    payload = request.get_json()
    print(payload)
    payload =payload["users"]
    #Running multiple consumers
    print(payload)
    create_user = KafkaUser(payload)
    msg=create_user.create_kafka_user()
    return msg

@app.route('/kafka-user/delete-user',methods=['POST'])
def delete_user():
    payload = request.get_json()
    print(payload)
    payload =payload["users"]
    #Running multiple consumers
    delete_user = KafkaUser(payload)
    msg=delete_user.delete_kafka_user()
    return msg

@app.route('/topic/produce/<int:count>',methods=['POST'])
def produce_oauth(count):
    payload = request.get_json()
    message =payload["message"]
    topic = payload["topics"]
    broker_type = request.args.get('type')
    #Running multiple consumers
    if broker_type == "oauth":
        broker = configuration.external_broker
    else:
        broker = configuration.broker
    iam_url = configuration.iam_uri
    producer = MessageProduceOauth(broker,topic,count,iam_url,configuration.client_id,configuration.client_psw,message,broker_type)
    msg=producer.secquence()
    return msg

@app.route('/startup-produce',methods=['GET'])
def startup_fun():
    message ="epljmmvpblphmbpeycekwpfrvrauvnpetijjusxuzccbgtoadkzubcveperaonsbqxkupssjtraoibmfanjdhfmdsjiqhxrinptwzkbxaldepunqcluplsryguufmidumzqcxeofwnjrfbnwkkxyyktentocytcoplunzhgjieuajcbqamedhqdrwqaorsojagjvxzbutkmzceiodposxhattktlzfpcywobpfuhntmfkfakjpnlbahxkhlqnqcvjmoqnajriilwlcatkvwkluzilwniqbskavvisrjhuheuatfjqyjnazxnkkizcrblernfyrxzpasfkrmwtxu"
    topic = ["test10"]
    broker = "eric-oss-dmm-kf-op-sz-kafka-bootstrap:9092"
    iam_url = configuration.iam_uri
    count = 10000000
    broker_type = "test"
    producer = MessageProduceStartup(broker,topic,count,iam_url,configuration.client_id,configuration.client_psw,message,broker_type)
    msg=producer.secquence()
    return msg

@app.route('/startup-consume',methods=['GET'])
def startup_consume():
    group ="Test"
    topic = ["test10"]
    broker = "eric-oss-dmm-kf-op-sz-kafka-bootstrap:9092"
    iam_url = configuration.iam_uri
    count = 10000000
    broker_type = "test"
    producer = MessageConsumeStartup(broker,topic,count,iam_url,configuration.client_id,configuration.client_psw,group,broker_type)
    msg=producer.secquence()
    return msg

@app.route('/topic/consume/<int:count>',methods=['POST'])
def consume_oauth(count):
    payload = request.get_json()
    group =payload["groups"]
    topic = payload["topics"]
    broker_type = request.args.get('type')
    #Running multiple consumers
    if broker_type == "oauth":
        broker = configuration.external_broker
    else:
        broker = configuration.broker
    iam_url = configuration.iam_uri
    consumer = MessageConsumeOauth(broker,topic,count,iam_url,configuration.client_id,configuration.client_psw,group,broker_type)
    msg=consumer.secquence()
    return msg


@app.route('/topic/consume/avro/<topic>/<int:count>',methods=['GET'])
def consume_avro(topic,count):
    app.logger.info(f'Request Method: {request.method}')
    app.logger.info(f'URL: {request.url}')
    app.logger.info(f'Request Data: {request.data.decode("utf-8")}')
    flow = request.args.get('flow')
    broker = configuration.broker
    if flow == "pm_counters":
        group_id = 'pm_counter_consumer'
        consumer1 = AvroRanMessageConsumer(broker,topic,group_id,count)
        msg=consumer1.activate_listener()
    elif flow == "4g_pm_events":
        group_id = '4g_consumer'
        consumer1 = Avro4GMessageConsumer(broker,topic,group_id,count)
        msg=consumer1.activate_listener()
    else:
        app.logger.error(f'Currently validating only PM_Counters and 4G_PM_Events flow')
        abort(400,"Accepting only pm_counters and 4g_pm_events query param")
        
    app.logger.info(f'Response for {request.url} Request - {msg}')
    return msg

@app.route('/topic/consume/proto/<topic>/<int:count>',methods=['GET'])
def consume_proto(topic,count):
    app.logger.info(f'Request Method: {request.method}')
    app.logger.info(f'URL: {request.url}')
    app.logger.info(f'Request Data: {request.data.decode("utf-8")}')    
    broker = configuration.broker
    group_id = '5g_pmevent'
    proto5GEvent = Proto5GGMessageConsumer(broker,topic,group_id,count)
    msg=proto5GEvent.start_consuming()
    app.logger.info(f'Response for {request.url} Request - {msg}')
    return msg

@app.route('/bdr/uploadfile/<bucket_name>', methods=['POST'])
def upload_file(bucket_name):
    #bucket_name = "ran-pm-counter-sftp-file-transfer"
    file_path = ""
    try:
        if 'file' in request.files:
            file = request.files['file']
            filename = secure_filename(file.filename)
            file_path = f"/var/tmp/{filename}"
            file.save(file_path)          
    except Exception as e:
        stack_trace = traceback.format_exc()
        return f"Error occurred while saving file : {e} \n{stack_trace}", 500
    print("file path "+file_path)
    response = Upload_file_into_BDR(bucket_name, file_path)
    return response 
     
    
@app.route('/bdr/create_bucket/<bucket_name>', methods=['GET'])
def create_bucket(bucket_name):
    response=Create_bucket(bucket_name)
    return response

@app.route('/topic/static-producer/<topic>',methods=['POST'])
def static_producer(topic):
    data=request.get_json()
    message_key=data["message_key"]
    raw_message = data["message"]
    message = json.dumps(raw_message)
    test=Static_Producer(configuration.broker,topic)
    result=test.producer(message_key,message)
    
    return result

@app.route('/topic/consume-on-key/<topic>',methods=['POST'])
def static_consumer(topic):
    data=request.get_json()
    desired_key=data["desired_key"]
    group_id = 'pm_counter_consumerstatic'
    #topic="eric-oss-3gpp-pm-xml-ran-parser-nr"
    consumer1 = AvroRanMessageConsumer_static(configuration.broker,topic,group_id)
    msg=consumer1.activate_listeners(desired_key)
    return msg
    
@app.route('/acmr-mock/deploy/<int:count>',methods=['POST'])
def deploy_request(count):
    data = request.get_json()
    payload = data["payload"]
    automationCompositionIds = data["automationCompositionIds"]
    acElementListIds = data["acElementListIds"]
    rAppIds = data["rAppIds"]
    test =  AcmrOperation(configuration.broker,"acmr-deploy-consumer",payload,count,automationCompositionIds,acElementListIds,rAppIds)        
    msg=test.start_deploy_thread()
    return msg

@app.route('/acmr-mock/undeploy/<int:count>',methods=['POST'])
def undeploy_request(count):
    data = request.get_json()
    payload = data["payload"]
    automationCompositionIds = data["automationCompositionIds"]
    test =  AcmrOperation(configuration.broker,"acmr-undeploy-consumer",payload,count,automationCompositionIds)        
    msg=test.start_undeploy_thread()
    return msg