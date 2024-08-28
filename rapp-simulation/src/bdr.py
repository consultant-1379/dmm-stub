import requests
import hmac
import hashlib
from datetime import datetime,timezone
from autz import ClientToken
from logger_config import logger
from flask import abort
import config
class bdr:
    def __init__(self):
        self.accesskeys = ClientToken()
        self.AWS_ACCESS_KEY_ID,self.AWS_SECRET_ACCESS_KEY,self.AWS_SESSION_TOKEN = self.accesskeys.retive_accesskeys()
        self.BDR_HOST = config.bdr_host
        self.BDR_URL = config.bdr_uri
        self.AMZ_DATE = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def generate_signature(self,method, canonical_uri, amz_date, bdr_host, aws_session_token,AWS_SECRET_ACCESS_KEY,AWS_ACCESS_KEY_ID):
        region = "us-east-1"
        date = datetime.now(timezone.utc).strftime("%Y%m%d")
        scope = f"{date}/{region}/s3/aws4_request"
        signed_headers = "host;x-amz-content-sha256;x-amz-date;x-amz-security-token"
        canonical_headers = f"host:{bdr_host}\nx-amz-content-sha256:UNSIGNED-PAYLOAD\nx-amz-date:{amz_date}\nx-amz-security-token:{aws_session_token}"
        canonical_request = f"{method}\n{canonical_uri}\n\n{canonical_headers}\n\n{signed_headers}\nUNSIGNED-PAYLOAD"
        sha256 = hashlib.sha256(canonical_request.encode()).hexdigest()
        string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{scope}\n{sha256}"

        secret_key = AWS_SECRET_ACCESS_KEY.encode()
        date_key = hmac.new(b"AWS4" + secret_key, date.encode(), hashlib.sha256).digest()
        date_region_key = hmac.new(date_key, region.encode(), hashlib.sha256).digest()
        date_region_service_key = hmac.new(date_region_key, b"s3", hashlib.sha256).digest()
        signing_key = hmac.new(date_region_service_key, b"aws4_request", hashlib.sha256).digest()
        signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()

        authorization = f"AWS4-HMAC-SHA256 Credential={AWS_ACCESS_KEY_ID}/{scope}, SignedHeaders={signed_headers}, Signature={signature}"
        return authorization

    def get_obj(self,URI):
        AUTHORIZATION = self.generate_signature("GET", URI, self.AMZ_DATE, self.BDR_HOST, self.AWS_SESSION_TOKEN, self.AWS_SECRET_ACCESS_KEY, self.AWS_ACCESS_KEY_ID)
        response = requests.get(self.BDR_URL + URI,
                            headers={
                                    "Authorization": AUTHORIZATION,
                                    "Host": self.BDR_HOST,
                                    "x-amz-content-sha256": "UNSIGNED-PAYLOAD",
                                    "X-Amz-Security-Token": self.AWS_SESSION_TOKEN,
                                    "x-amz-date": self.AMZ_DATE
                                },
                                verify=config.platformcaCertFileFullPath)
        if response.status_code == 200:
            return response.text 
        else:
            logger.error(f"failed to read object :: {response.status_code}")
            abort(response.status_code, f"failed to read object")
    def list_obj(self,URI):
        AUTHORIZATION = self.generate_signature("GET", URI, self.AMZ_DATE, self.BDR_HOST, self.AWS_SESSION_TOKEN,self.AWS_SECRET_ACCESS_KEY,self.AWS_ACCESS_KEY_ID)
        response = requests.get(self.BDR_URL + URI,
                                headers={
                                    "Authorization": AUTHORIZATION,
                                    "Host": self.BDR_HOST,
                                    "x-amz-content-sha256": "UNSIGNED-PAYLOAD",
                                    "X-Amz-Security-Token": self.AWS_SESSION_TOKEN,
                                    "x-amz-date": self.AMZ_DATE
                                },
                                verify=config.platformcaCertFileFullPath)
        if response.status_code == 200:
            return response.text
        else:
            logger.error(f"failed to list a object :: {response.status_code}")
            abort(response.status_code, f"failed to list object")
            
    def write_obj(self,URI,file):
        AUTHORIZATION = self.generate_signature("PUT", URI, self.AMZ_DATE, self.BDR_HOST, self.AWS_SESSION_TOKEN,self.AWS_SECRET_ACCESS_KEY,self.AWS_ACCESS_KEY_ID)
        response = requests.put(self.BDR_URL + URI,
                            headers={
                                "Authorization": AUTHORIZATION,
                                "Host": self.BDR_HOST,
                                "x-amz-content-sha256": "UNSIGNED-PAYLOAD",
                                "X-Amz-Security-Token": self.AWS_SESSION_TOKEN,
                                "x-amz-date": self.AMZ_DATE,
                                "Content-Type": "text"
                            },
                            data=open(file, "rb"),
                            verify=config.platformcaCertFileFullPath)
        if response.status_code == 200:
            return f"sucessfully uploded a object"
        else:
            logger.error(f"failed to upload object :: {response.status_code}")
            abort(response.status_code, f"failed to upload object") 

    def delete_obj(self,URI):
        AUTHORIZATION = self.generate_signature("DELETE", URI, self.AMZ_DATE, self.BDR_HOST, self.AWS_SESSION_TOKEN,self.AWS_SECRET_ACCESS_KEY,self.AWS_ACCESS_KEY_ID)
        response = requests.delete(self.BDR_URL + URI,
                                headers={
                                    "Authorization": AUTHORIZATION,
                                    "Host": self.BDR_HOST,
                                    "x-amz-content-sha256": "UNSIGNED-PAYLOAD",
                                    "X-Amz-Security-Token": self.AWS_SESSION_TOKEN,
                                    "x-amz-date": self.AMZ_DATE
                                },
                                verify=config.platformcaCertFileFullPath)
        if response.status_code == 204:
            return f"sucessfully object deleted"
        else:
            logger.error(f"failed to delete object :: {response.status_code}")
            abort(response.status_code, f"failed to delete object") 
    