import requests
from logger_config import logger
import json
import time
class DataCatalog:

    def register_fileformat(self):
        while True:
            data = {
                    "dataSpace": {
                        "name": "15G"
                    },
                    "dataService": {
                        "dataServiceName": "kafka-wrapper"
                    },
                    "dataCategory": {
                        "dataCategoryName": "app-eng-PM_state"
                    },
                    "dataProviderType": {
                        "dataProviderName": "wrapper"
                    },
                    "messageStatusTopic": {
                        "name":  "streams_topic",
                        "messageBusId": 1,
                        "specificationReference": "SpecRef101",
                        "encoding": "JSON"
                    },
                    "messageDataTopic": {
                        "name": "streams_topic",
                        "messageBusId": 1,
                        "encoding": "JSON"
                    },
                    "dataServiceInstance": {
                        "dataServiceInstanceName": "dsinst1011",
                        "controlEndPoint": "http://localhost:8082",
                        "consumedDataSpace": "",
                        "consumedDataCategory": "",
                        "consumedDataProvider": "",
                        "consumedSchemaName": "",
                        "consumedSchemaVersion": ""
                    },
                    "dataType": {
                        "mediumType": "stream",
                        "schemaName": "RANSCHEMA",
                        "schemaVersion": "3",
                        "isExternal": True,
                        "consumedDataSpace": "",
                        "consumedDataCategory": "",
                        "consumedDataProvider": "",
                        "consumedSchemaName": "",
                        "consumedSchemaVersion": ""
                    },
                    "supportedPredicateParameter": {
                        "parameterName": "pd1011",
                        "isPassedToConsumedService": True
                    },
                    "messageSchema": {
                        "specificationReference": "SpecRef2020"
                    }
                }
            headers = {
                "Content-Type": "application/json"
            }
            try:
                response = requests.put('http://eric-oss-data-catalog:9590/catalog/v1/message-schema', json=data,headers=headers)
                if response.status_code == 201 or response.status_code == 200 or response.status_code == 409:
                    logger.info(f'Data type register sucessfully ::  {response.status_code} :: {response.text}')
                    break
                else:
                    logger.error(f'Fail to register data type :: {response.status_code} :: {response.text}')
                    time.sleep(5)
            except requests.exceptions.RequestException as e:
                logger.error(f'exception occure while registering data type :: {e}')
    
    def retrive_subscription(self):
        condition = True
        while condition:
            try:
                headers = {
                    "Content-Type": "application/json"
                }
                response = requests.get('http://eric-oss-data-catalog:9590/catalog/v3/subscriptions?serviceName=kafka-wrapper',headers=headers)
                availableSub = len(json.loads(response.text))
                if response.status_code == 200 and len(json.loads(response.text)) != 0:
                    logger.info(f'subscription available for data type  ::  {response.status_code} :: {response.text}')
                    logger.info(f'available subscription count :: {availableSub} :: {json.loads(response.text)}')
                    while condition:
                        response = requests.get('http://eric-oss-data-catalog:9590/catalog/v3/subscriptions?serviceName=kafka-wrapper',headers=headers)
                        if response.status_code == 200:
                            if len(json.loads(response.text)) > availableSub:
                                condition = False
                            logger.info(f'Retry :: available subscription count :: {availableSub} :: {json.loads(response.text)}')
                            time.sleep(5)
                elif response.status_code == 200 and len(json.loads(response.text)) == 0:
                    logger.info(f'subscription not available for data type  :: {response.status_code} :: {response.text}')
                    while condition:
                        response = requests.get('http://eric-oss-data-catalog:9590/catalog/v3/subscriptions?serviceName=kafka-wrapper',headers=headers)
                        if response.status_code == 200 and len(json.loads(response.text)) != 0:
                            condition = False
                        logger.info(f'Retry :: available subscription count :: {availableSub} :: {json.loads(response.text)}')
                        time.sleep(5)
                else:
                    logger.error(f'subscription not available for data type  :: {response.status_code} :: {response.text}')
            except requests.exceptions.RequestException as e:
                logger.error(f'exception occure retrive subscriiption :: {e}')