import requests
import xml.etree.ElementTree as ET
from logger_config import logger
import config
class ClientToken:     
    def retrieve_token(self):
        try:
            payload = {
                'grant_type': 'client_credentials'
            }
            resp = requests.post(config.iam_uri, verify=config.platformcaCertFileFullPath,
                                auth=(config.client_id,config.client_psw),
                                data=payload)
            resp.raise_for_status()  # Raise an exception for bad status codes
            token = resp.json()
            access_token = token['access_token']
            if access_token:
                logger.info("Token successfully retrieved")
                return access_token
            else:
                logger.error("Access token not found in response.")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred while retrieving token for client: {config.client_id} Error: {e}")
            return None
        except KeyError:
            logger.error(f"Token response format is unexpected for client: {config.client_id}")
            return None

    def token_exchange(self):
        try:
            token = self.retrieve_token()
            if token is None:
                raise ValueError("Token retrieval failed or returned None")
            payload = {
                'WebIdentityToken': token,
                "Action": "AssumeRoleWithWebIdentity",
                "Version": "2011-06-15",
                "DurationSeconds": 5000
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            resp = requests.post(config.bdr_uri, verify=config.platformcaCertFileFullPath,
                                data=payload,headers=headers)
            resp.raise_for_status()
            return resp.text
        except ValueError as e:
            logger.error(f"Token exchange failed for client: {config.client_id}. Error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Token exchange failled for client: {config.client_id}. Error: {e}")
            return None

    def retive_accesskeys(self):
        accesskeyId=None
        secretAcessKey=None
        sessionToken=None
        try:
            token=self.token_exchange()
            root = ET.fromstring(token)
            for idenity in root.findall('{https://sts.amazonaws.com/doc/2011-06-15/}AssumeRoleWithWebIdentityResult'):
                for credential in idenity.findall('{https://sts.amazonaws.com/doc/2011-06-15/}Credentials'):
                    accesskeyId=credential.find('{https://sts.amazonaws.com/doc/2011-06-15/}AccessKeyId').text
                    secretAcessKey=credential.find('{https://sts.amazonaws.com/doc/2011-06-15/}SecretAccessKey').text
                    sessionToken=credential.find('{https://sts.amazonaws.com/doc/2011-06-15/}SessionToken').text
            return accesskeyId , secretAcessKey,sessionToken
        except ET.ParseError as parse_error:
            logger.info(f"XML parsing error: {parse_error}")
            return None, None, None
        except Exception as e:
            # Handle any other exceptions
            logger.info(f"An error occurred: {e}")
            return None, None, None

