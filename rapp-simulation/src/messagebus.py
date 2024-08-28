import requests
import logging
import json
from config import platformcaCertFileFullPath ,client_id ,namespace
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO)
class datacatalog:
    logger = logging.getLogger(__name__)

    def __init__(self,username ,password,hostname):
        self.username = username
        self.password = password
        self.hostname = hostname        

    def auth_token(self):

        headers = {
            "X-Login": self.username,
            "X-password": self.password,
        }
        resp = requests.post(self.hostname+"/auth/v1/login",verify=platformcaCertFileFullPath,
                            headers=headers)
        return resp.text
    
    def subscription_notificationTopic(self):
        token = self.auth_token()
        headers = {
            'Cookie': 'JSESSIONID='+token
        }
        res = requests.get(self.hostname+"/dmm-data-catalog/catalog/v1/subscription-message-data-topic/?rAppId="+client_id,verify=platformcaCertFileFullPath,headers=headers)
        response= res.json()
        response=response.get("subscriptions")
        print(f"Response  : {response[0]}")
        topics = response[0].get("topics")
        topic=topics[0]
        self.logger.info(f"topic name in function - {topic}")
        return topic
 
    def data_type(self):
        token = self.auth_token()
        headers = {
            'Cookie': 'JSESSIONID='+token
        }
        res = requests.get(self.hostname+"/dmm-data-catalog/catalog/v1/data-type?isExternal=true&dataSpace=4G&dataCategory=PM_COUNTERS&dataProvider=RAN",verify=platformcaCertFileFullPath,headers=headers)
        print(res.text)       
    def subscription(self):
        token = self.auth_token()
        headers = {
            'Cookie': 'JSESSIONID='+token
        }
        res = requests.get(self.hostname+"/dmm-data-catalog/catalog/v1/subscriptions/?rAppId="+client_id,verify=platformcaCertFileFullPath,headers=headers)
        status=res.json()
        # status1=status[0][status]
        activeSubscriptinCount=0
        inactiveSubscriptinCount=0
        if len(status) != 0:
            self.logger.info(f"Total subscription count : {len(status)}")
            for sub in status:
                subscriptionStatus= sub.get('status')  
                if subscriptionStatus == "Active":
                    activeSubscriptinCount +=1
                else:
                    inactiveSubscriptinCount +=1
            if len(status) == activeSubscriptinCount:
                self.logger.info(f"All subscriptions are Active currently")
            else:
                self.logger.error(f"{inactiveSubscriptinCount} subscriptions are inactive")
        else:
            self.logger.error(f"There is no subscription for client ID  - {client_id}")
        return activeSubscriptinCount
                
    def external_broker(self):
        token = self.auth_token()
        headers = {
            'Cookie': 'JSESSIONID='+token
        }
        external_host = ""
        try:
            res = requests.get(self.hostname+"/dmm-data-catalog/catalog/v1/message-bus?name=eric-oss-dmm-kf-op-sz-kafka-bootstrap&nameSpace="+namespace,verify=platformcaCertFileFullPath,headers=headers)
            res.raise_for_status()
            try:
                response= res.json()
                if isinstance(response, list) and len(response) > 0:
                    endpoints=response[0].get("accessEndpoints")
                    for endpoint in endpoints:
                        if endpoint.endswith(":443"):
                            external_host=endpoint
                else:
                    self.logger.error("Unexpected response format. Expected a non-empty list.")
            except (IndexError, KeyError) as e:
                self.logger.error(f"Error while fetch external host from response body - {e}")
        except requests.exceptions.HTTPError as http_err:
            status_code = res.status_code
            error_message = res.text
            self.logger.error(f"Error while fetching external bootstrap host from data catalog - {status_code} - response body {error_message}" )
        return external_host
