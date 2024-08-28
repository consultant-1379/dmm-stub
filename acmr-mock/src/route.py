from time import sleep
import json
from flask import Flask,jsonify,abort,request
from producer_oauth import MessageProduceOauth
from consumer_oauth import MessageConsumeOauth
import requests
import os
import logging
import configuration
import uuid

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})



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