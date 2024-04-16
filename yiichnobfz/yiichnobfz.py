import ibm_boto3
from botocore.client import Config
import os

COS_API_KEY = os.getenv("cos_api_key")
SERVICE_INSTANCE_ID = os.getenv("service_instance_id")
COS_AUTH_ENDPOINT = os.getenv('cos_auth_enpoint')
COS_SERVICE_ENDPOINT = os.getenv('cos_service_endpoint')
COS_BUCKET_NAME = os.getenv('cos_bucket_name')
DIRECTORY = os.getenv('directory')


def init_cos(api_key:str, service_instance_id:str=SERVICE_INSTANCE_ID):
        """Initialize a COS client
        """
        cos = (ibm_boto3
               .client('s3',
                       ibm_api_key_id=api_key,
                       ibm_service_instance_id=service_instance_id,
                       config=Config(signature_version='oauth'),
                       endpoint_url=COS_SERVICE_ENDPOINT))
        return cos

cos_client = init_cos(COS_API_KEY)


def download_cos_directory(cos_client, bucket_name, cos_directory, local_directory):
    paginator = cos_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=cos_directory)
    for page in pages:
        for obj in page.get('Contents', []):
            # Create local file path
            local_file_path = local_directory + obj['Key'][len(cos_directory):]
            # Create local directory if it doesn't exist
            local_file_directory = '/'.join(local_file_path.split('/')[:-1])
            if not os.path.exists(local_file_directory):
                os.makedirs(local_file_directory)
            # Download the object
            cos_client.download_file(bucket_name, obj['Key'], local_file_path)
            
download_cos_directory(cos_client, COS_BUCKET_NAME, DIRECTORY, DIRECTORY)
            