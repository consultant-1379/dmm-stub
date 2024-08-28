from minio import Minio
from minio.error import S3Error
from logger_config import logger
import os
import configuration
from flask import abort


def Upload_file_into_BDR(bucket_name, file_path):
    # Set to True if MinIO server uses HTTPS, otherwise False
    secure=False
    # bucket_name = 'ran-pm-counter-sftp-file-transfer'
    
    try:
        # Initialize MinIO client object
        client = Minio(configuration.minio_endpoint, access_key=configuration.access_key, secret_key=configuration.secret_key,secure=secure)
        # Specify the path of the file to upload
        
        # file_path = '/kafka-wrapper/resources/testfile.xml.gz'
        _, object_name = os.path.split(file_path)
         

        # Specify the name to the file in the bucket
        # object_name = 'testfile.xml.gz'

        # Upload the file to MinIO
        response=client.fput_object(bucket_name, object_name, file_path)
        return f"File '{object_name}' uploaded successfully to bucket '{bucket_name}'."

    except S3Error as err:
        # S3-specific error
        abort(400,f"Failed to connect to MinIO server: {err}")
    except Exception as err:
        # Other errors
        abort(400,f"An error occurred: {err}")
        
        
def Create_bucket(bucket_name):
    # Set to True if MinIO server uses HTTPS, otherwise False
    secure=False
    # bucket_name = 'ran-pm-counter-sftp-file-transfer'
    
    try:
        # Initialize MinIO client object
        client = Minio(configuration.minio_endpoint, access_key=configuration.access_key, secret_key=configuration.secret_key,secure=secure)
        # Specify the path of the file to upload
        

        response=client.make_bucket(bucket_name)
        return f"Bucket created sucessfully {bucket_name}."
    except S3Error as err:
        # S3-specific error
        abort(400,f"Failed to connect to MinIO server: {err}")
    except Exception as err:
        # Other errors
        abort(400,f"An error occurred: {err}")

    
                   








