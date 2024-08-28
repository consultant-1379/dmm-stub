from flask import Flask,jsonify
from route import app
from unpackage import unpack
import configuration
import threading
import time
from post_startup import start_kafka_client
from acmr_consume_startup import AcmrConsumerStartUp
from adc_startup_script import consume_from_adctopics
import multiprocessing
import uuid
from healthcheck import healthCheck
if __name__ == '__main__':
    if configuration.load == "true":
        test_thread = threading.Thread(target=start_kafka_client)
        test_thread.start()
        time.sleep(10)
    elif configuration.acmr_mock == "true":
        initial = AcmrConsumerStartUp(configuration.broker,str(uuid.uuid4()),True)
        test_thread = multiprocessing.Process(target=initial.consume_from_topic)
        test_thread.start()
        time.sleep(10)
    if configuration.adcload == "true":
        adctest_thread = threading.Thread(target=consume_from_adctopics)
        adctest_thread.start()
        time.sleep(10)
    app.run(host='0.0.0.0',port="8082")
