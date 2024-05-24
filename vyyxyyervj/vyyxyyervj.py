import json
from io import BytesIO
import pandas as pd
import ibm_boto3
from ibm_botocore.client import Config as BotoConfig
from ibm_botocore.client import ClientError


class COSClient:
    def __init__(self):
        self.cos_credentials = {
            "cos_instance_crn": COS_RESOURCE_INSTANCE_ID,
            "endpoint": COS_ENDPOINT_URL,
            "ibm_auth_endpoint": "https://iam.cloud.ibm.com/identity/token",
            "api_key_id": COS_API_KEY,
            "bucket": COS_BUCKET,
        }

        self.cos_client = ibm_boto3.client(
            service_name = "s3",
            ibm_api_key_id = self.cos_credentials["api_key_id"],
            ibm_service_instance_id = self.cos_credentials["cos_instance_crn"],
            ibm_auth_endpoint = self.cos_credentials["ibm_auth_endpoint"],
            config = BotoConfig(signature_version = "oauth"),
            endpoint_url = self.cos_credentials["endpoint"]
        )


    def get_object(self, object_name, bucket_name=COS_BUCKET):
        # Retrieve an object from COS
        try:
            response = self.cos_client.get_object(Bucket = bucket_name , Key = object_name)
            return response
        except Exception as e:
            print(f"An error occurred while retrieving the object: {e}")
            return None


    def download_file_from_cos(self, object_key, local_file_name, bucket_name=COS_BUCKET):
        # Download a file from COS
        try:
            res = self.cos_client.download_file(Bucket = bucket_name, 
                                                   Key = object_key, Filename = local_file_name)
        except Exception as e:
            print(f"An error occurred while downloading the object: {e}")
        else:
            print(f'File downloaded from {bucket_name} to local file named {local_file_name}')


    def list_all_objects(self, bucket_name=COS_BUCKET):
        # List all objects in the bucket
        all_objects = []
        try:
            paginator = self.cos_client.get_paginator('list_objects_v2')
            for result in paginator.paginate(Bucket = bucket_name):
                if 'Contents' in result:
                    all_objects.extend(result['Contents'])
            print("Total number of objects:", len(all_objects))
        except Exception as e:
            print(f"An error occurred while listing the objects: {e}")
        return all_objects


    def upload_fileobj(self, file_stream, object_name, bucket_name=COS_BUCKET):
        # Use the COS client to upload a file-like object to the specified bucket
        try:
            self.client.upload_fileobj(
                Fileobj=file_stream,
                Bucket=bucket_name,
                Key=object_name
            )
            print(f"File uploaded successfully to: {object_name}")
        except Exception as e:
            print(f"An error occurred: {e}")


    def file_exists_in_cos(self, filename, bucket_name=COS_BUCKET):
        # Check if a filename exists in COS or not
        try:
            self.cos_client.head_object(Bucket=bucket_name, Key=filename)
            return True
        except:
            return False
        
    
    def put_object(self, data, filename, bucket_name=COS_BUCKET):
        # Make a PUT request
        try:
            self.cos_client.put_object(Bucket=bucket_name, Key=filename, Body=data)
            print(f"File uploaded successfully to: {filename}")
        except Exception as e:
            print(f"An error occurred: {e}")


class COSClientV2:
    def __init__(self):
        self.cos_client = ibm_boto3.client(
            service_name = "s3",
            aws_access_key_id = COS_HMAC_ACCESS_KEY_ID,
            aws_secret_access_key = COS_HMAC_SECRET_ACCESS_KEY,
            endpoint_url = COS_ENDPOINT_URL
        )

    def generate_url_for_object(self, key_name, bucket_name=COS_BUCKET):
        # Generate a temporary url for object
        try:
            http_method = 'get_object'
            expiration = 3600             
            signedUrl = self.cos_client.generate_presigned_url(http_method, Params = {'Bucket': bucket_name, 
                                                                                      'Key': key_name}, 
                                                                                      ExpiresIn = expiration)
            return signedUrl
        except Exception as e:
            print(f"An error occurred while creating the url: {e}")
            return None