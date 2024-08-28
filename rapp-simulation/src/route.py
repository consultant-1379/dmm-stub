from time import sleep
import json
from flask import Flask,jsonify,abort,request
import requests
import os
import logging
from bdr import bdr
from prometheus_client import generate_latest
from werkzeug.utils import secure_filename
app = Flask(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO)

@app.route('/metrics')
def prometheus_metrics():
    return generate_latest() 

@app.route('/write-object/<obj>', methods=['POST'])
def upload_object(obj):
    obj_path="/rapp-simulation-test/"+obj
    file_path="/var/tmp/text.py"
    try:
        if 'file' in request.files:
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(file_path)  
            bdr_obj = bdr()
            value=bdr_obj.write_obj(obj_path, file_path)
            return value
    except Exception as e:
        return "Error occurred while processing the request", 500
    

@app.route('/list-object', methods=['GET'])
def list_object():
    obj_path="/rapp-simulation-test/"
    bdr_obj =bdr()
    value=bdr_obj.list_obj(obj_path)
    return value
        

@app.route('/get-object/<obj>', methods=['GET'])
def get_object(obj):
    obj_path="/rapp-simulation-test/"+obj
    bdr_obj =bdr()
    value=bdr_obj.get_obj(obj_path)
    return value

@app.route('/delete-object/<obj>', methods=['GET'])
def delete_object(obj):
    obj_path="/rapp-simulation-test/"+obj
    bdr_obj =bdr()
    value=bdr_obj.delete_obj(obj_path)
    return value