from flask import Flask,jsonify
from route import app
from startup import start_listener
from exposure import ApiExposure
import os
import config
import urllib3
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
if __name__ == '__main__':
    consumer = start_listener()
    consumer.start_consumer()
    api = ApiExposure()
    api.app_service_exposure()
    api.access_control()
    app.run(host='0.0.0.0',port=8082)
