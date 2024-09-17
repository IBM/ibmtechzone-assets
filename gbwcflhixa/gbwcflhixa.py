import json
from io import BytesIO
import pandas as pd
import ibm_boto3
from ibm_botocore.client import Config as BotoConfig
from ibm_botocore.client import ClientError
import os
from dotenv import load_dotenv


load_dotenv()

class COSClient:
    def __init__(self):
        self.cos_credentials = {
            # os.environ["project_name"]
            "cos_instance_crn": os.environ["cos_instance_crn"],
            "endpoint": os.environ["endpoint"],
            "ibm_auth_endpoint": os.environ["ibm_auth_endpoint"],

            "api_key_id": os.environ["api_key_id"],
            "bucket": os.environ["bucket"],
        }

        self.cos_client = ibm_boto3.client(
            service_name = "s3",
            ibm_api_key_id = self.cos_credentials["api_key_id"],
            ibm_service_instance_id = self.cos_credentials["cos_instance_crn"],
            ibm_auth_endpoint = self.cos_credentials["ibm_auth_endpoint"],
            config = BotoConfig(signature_version = "oauth"),
            endpoint_url = self.cos_credentials["endpoint"]
        )


    def get_object(self, object_name):
        # Retrieve an object from COS
        try:
            response = self.cos_client.get_object(Bucket = self.cos_credentials["bucket"] , Key = object_name)
            return response
        except Exception as e:
            print(f"An error occurred while retrieving the object: {e}")
            return None


    def download_file_from_cos(self, object_key, local_file_name):
        # Download a file from COS
        try:
            res = self.cos_client.download_file(Bucket = self.cos_credentials["bucket"], 
                                                   Key = object_key, Filename = local_file_name)
            # return res
        except Exception as e:
            print(f"An error occurred while downloading the object: {e}")
        else:
            print(f'File downloaded from {self.cos_credentials["bucket"]} to local file named {local_file_name}')

   


    def list_all_objects(self):
        # List all objects in the bucket
        all_objects = []
        try:
            paginator = self.cos_client.get_paginator('list_objects_v2')
            for result in paginator.paginate(Bucket = self.cos_credentials["bucket"]):
                if 'Contents' in result:
                    all_objects.extend(result['Contents'])
            print("Total number of objects:", len(all_objects))
        except Exception as e:
            print(f"An error occurred while listing the objects: {e}")
        return all_objects
    
    def upload_fileobj(self, file_stream, object_name):
    #Use the COS client to upload a file-like object to the specified bucket
        try:
            self.cos_client.upload_fileobj(
                Fileobj=file_stream,
                Bucket=self.cos_credentials["bucket"],
                Key=object_name
            )
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_object(self ,bucket_name, object_name):
        # Create a COS client configuration
        try:
            # Delete the object
            response = self.cos_client.delete_object(Bucket=bucket_name, Key=object_name)
            print("Object deleted successfully from bucket", bucket_name)
        except ClientError as be:
            print("ClientError:", be)
        except Exception as e:
            print("Unable to delete object:", e)


def is_valid_file_type(filename):
    return filename.lower().endswith(('.csv', '.xlsx', '.pdf','.txt'))

if __name__ == "__main__":
    cos_client = COSClient()

    while True:
        print("\nChoose an action:")
        print("1. Upload a file")
        print("2. Download a file")
        print("3. List all files")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            file_path = input("Enter the path of the file to upload: ")
            if os.path.exists(file_path) and is_valid_file_type(file_path):
                file_name = os.path.basename(file_path)
                with open(file_path, 'rb') as file_obj:
                    cos_client.upload_fileobj(file_obj, file_name)
            else:
                print("Invalid file or unsupported file type. Please use .csv, .xlsx, or .pdf files.")

        elif choice == '2':
            file_name = input("Enter the name of the file to download: ")
            if is_valid_file_type(file_name):
                local_file_name = input("Enter the name to save the file as: ")
                cos_client.download_file_from_cos(file_name, local_file_name)
            else:
                print("Invalid file type. Please use .csv, .xlsx, or .pdf files.")

        elif choice == '3':
            objects = cos_client.list_all_objects()
            for obj in objects:
                print(obj['Key'])

        elif choice == '4':
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")