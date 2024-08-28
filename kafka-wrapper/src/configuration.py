import os
from logger_config import logger

external_broker = os.environ.get('BOOTSTRAP_EXTERNAL')+":443"
broker = os.environ.get('BROKER')
namespace = os.environ.get('NAMESPACE')
iam_uri = "https://"+os.environ.get('IAM_URI')+"/auth/realms/master/protocol/openid-connect/token"
client_id = os.environ.get('CLIENT_ID')
client_psw = os.environ.get('CLIENT_PSW')
count = int(os.environ.get('COUNT'))
size = int(os.environ.get('SIZE'))
topic_count = int(os.environ.get('TOPIC_COUNT'))
messageCount_topic = round(count / topic_count)
load = os.environ.get('LOAD')
access_key =  os.environ.get('BDR_ACCESS_KEY')
secret_key =  os.environ.get('BDR_SECRET_KEY')
acmr_mock = os.environ.get('ACMR_MOCK')
adcload = os.environ.get('ADC_LOAD')
topicbuffertime = int(os.environ.get('TOPICBUFFERTIME'))
minio_endpoint = "eric-data-object-storage-mn:9000"
acmr_topic = os.environ.get("ACMR_TOPIC")


def gettopicsfromenv():

    # from deployment env variables
    adctopics = []
    index = 0
    while True:
        topicname = os.environ.get(f'ADCTOPICS_{index}')
        if topicname is None:
            break
        adctopics.append(topicname)
        index += 1

    logger.info(f" Array values from deployment env variable {adctopics}")
    return adctopics