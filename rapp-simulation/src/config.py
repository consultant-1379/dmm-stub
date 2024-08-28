import os

namespace = os.environ.get('NAMESPACE')
iam_uri = os.environ.get('IAM_URI')
gas_uri = os.environ.get('GAS_URI')
bdr_uri = os.environ.get('BDR_URI')
bdr_host = os.environ.get('BDR_HOST')
client_id = os.environ.get('CLIENT_ID')
client_psw = os.environ.get('CLIENT_PSW')
platformSecretName = os.environ.get('platformSecretName')
platformcaCertFileName = os.environ.get('platformcaCertFileName')
platformcaCertMountPath = os.environ.get('platformcaCertMountPath')
platformcaCertFileFullPath = platformcaCertMountPath +"/"+ platformcaCertFileName
kafkaSecretName = os.environ.get('kafkaSecretName')   
kafkacaCertFileName = os.environ.get('kafkacaCertFileName')
kafkacaCertMountPath = os.environ.get('kafkacaCertMountPath')
kafkacaCertFileFullPath = kafkacaCertMountPath +"/"+ kafkacaCertFileName
userName = os.environ.get('userName')
userPassword = os.environ.get('userPassword')