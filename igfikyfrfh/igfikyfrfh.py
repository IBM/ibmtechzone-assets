#Install these libraries first
# pip install numpy
# pip install ibm_boto3
# pip install ibm_cloud_sdk_core
# pip install ibm_watson_openscale
# pip install pandas



#Import libraries
import os, types
import pandas as pd
from botocore.client import Config
import ibm_boto3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson_openscale import APIClient
from ibm_watson_openscale.supporting_classes.enums import DataSetTypes, TargetTypes,ResponseTypes
from ibm_watson_openscale.supporting_classes.payload_record import PayloadRecord
import time
import requests
import numpy as np


#Credentials needed 

cos_client = ibm_boto3.client(service_name='s3',
    ibm_api_key_id='<EDIT THIS>',
    ibm_auth_endpoint="https://iam.cloud.ibm.com/identity/token",
    config=Config(signature_version='oauth'),
    endpoint_url='<EDIT THIS>')

bucket_name = '<EDIT THIS>'



service_credentials = {
				"apikey": "<EDIT THIS>",
				"url": "<EDIT THIS>"
			}

authenticator = IAMAuthenticator(
		apikey=service_credentials["apikey"],
		url="https://iam.cloud.ibm.com/identity/token"
	)

SERVICE_INSTANCE_ID = "<EDIT THIS>"
wos_client = APIClient(authenticator=authenticator, service_instance_id=SERVICE_INSTANCE_ID, service_url=service_credentials["url"])

SUBSCRIPTION_ID = "<EDIT THIS>"# Monitor



PROJECT_ID = "<EDIT THIS>"
IBM_CLOUD_URL = "<EDIT THIS>"
API_KEY = "<EDIT THIS>"
IAM_URL="https://iam.ng.bluemix.net/oidc/token"
OPENSCALE_API_URL = "https://api.aiopenscale.cloud.ibm.com"

data_mart_id="<EDIT THIS>"

#Function to automate uploading data to Governance


def process_and_store_llm_data(bucket_name, subscription_id,data_mart_id, openscale_api_url):
    
    
    def get_access_token():
        parms = {
        "url": OPENSCALE_API_URL,
        "iam_url": IAM_URL,
        "apikey": API_KEY
    }
        
        url = parms['iam_url']
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": parms['apikey']
        }
        response = requests.post(url, data=data, headers=headers)
        json_data = response.json()
        access_token = json_data['access_token']
        return access_token
    
    def list_all_objects(bucket_name):
        all_objects = []
        try:
            paginator = cos_client.get_paginator('list_objects_v2')
            for result in paginator.paginate(Bucket=bucket_name):
                if 'Contents' in result:
                    all_objects.extend(result['Contents'])
            print("Total number of objects:", len(all_objects))
        except Exception as e:
            print(f"An error occurred while listing the objects: {e}")
        return all_objects

    def get_latest_csv_file_key(bucket_name):
        try:
            response = cos_client.list_objects_v2(Bucket=bucket_name)
            files = response.get('Contents', [])
            csv_files = [file for file in files if file['Key'].endswith('.csv')]
            
            if not csv_files:
                return None
            
            latest_csv_file = max(csv_files, key=lambda x: x['LastModified'])
            return latest_csv_file['Key']
        except ClientError as e:
            print(f"ClientError: {e.response['Error']['Message']}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return None

    def store_llm_data_as_payload(subscription_id, llm_data):
        payload_data_set_id = None
        payload_data_set_list = wos_client.data_sets.list(
            type=DataSetTypes.PAYLOAD_LOGGING,
            target_target_id=subscription_id,
            target_target_type=TargetTypes.SUBSCRIPTION
        ).result.data_sets
        
        if payload_data_set_list:
            payload_data_set_id = payload_data_set_list[0].metadata.id
        
        if payload_data_set_id is None:
            print("Payload data set not found. Please check subscription status.")
            return
        
        print("Payload data set id:", payload_data_set_id)
        
        input_text_list_of_lists = llm_data['query'].apply(lambda x: [x]).tolist()
        generated_summary_list_of_lists = llm_data['answer'].apply(lambda x: [x]).tolist()
        
        scoring_request = {
            "fields": ["query"],
            "values": input_text_list_of_lists
        }
        
        scoring_response = {
            "predictions": [
                {
                    "fields": ["answer"],
                    "values": generated_summary_list_of_lists
                }
            ]
        }
        
        records_list = []
        pl_record = PayloadRecord(request=scoring_request, response=scoring_response)
        records_list.append(pl_record)
        
        wos_client.data_sets.store_records(data_set_id=payload_data_set_id, request_body=records_list)
        time.sleep(10)
        pl_records_count = wos_client.data_sets.get_records_count(payload_data_set_id)
        print("Number of records in the payload logging table: {}".format(pl_records_count))
        if pl_records_count == 0:
            raise Exception("Payload logging did not happen!")
    
    
        records = wos_client.data_sets.get_list_of_records(data_set_id=payload_data_set_id, output_type=ResponseTypes.PANDAS).result
        print(records.head())
        
        return payload_data_set_id

    def store_llm_data_as_feedback(subscription_id, llm_data, access_token, data_mart_id, openscale_api_url):
        # wos_client.subscriptions.create_feedback_table(subscription_id=subscription_id)
        
        feedback_dataset_id = None
        feedback_dataset = wos_client.data_sets.list(type=DataSetTypes.FEEDBACK, 
                                                        target_target_id=subscription_id, 
                                                        target_target_type=TargetTypes.SUBSCRIPTION).result
        print(feedback_dataset)
        feedback_dataset_id = feedback_dataset.data_sets[0].metadata.id
        if feedback_dataset_id is None:
            print("Feedback data set not found. Please check quality monitor status.")
            
        fields = llm_data.columns.tolist()
        values = llm_data.values.tolist()
        feedback_payload = {"fields": fields, "values": values}
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }

        datasets_store_records_url = "{}/openscale/{}/v2/data_sets/{}/records".format(openscale_api_url, data_mart_id, feedback_dataset_id)

        response = requests.post(datasets_store_records_url, json=feedback_payload, headers=headers, verify=False)
        json_data = response.json()
        print(json_data)
        
        time.sleep(10)
        DATASETS_STORE_RECORDS_URL =   OPENSCALE_API_URL + "/openscale/{0}/v2/data_sets/{1}/records?limit={2}&include_total_count={3}".format(data_mart_id, feedback_dataset_id, 1, "true")
        response = requests.get(DATASETS_STORE_RECORDS_URL, headers=headers, verify=False)
        json_data = response.json()
        print(json_data['total_count'])
        
        feedback_records = wos_client.data_sets.get_list_of_records(data_set_id=feedback_dataset_id, output_type=ResponseTypes.PANDAS).result
        print(feedback_records.head())

    # List all objects in the bucket (for logging purposes)
    list_all_objects(bucket_name)

    # Get the latest CSV file key
    object_key = get_latest_csv_file_key(bucket_name)
    if object_key is None:
        print("No CSV files found in the bucket.")
        return

    # Fetch the latest CSV file and read it into a DataFrame
    body = cos_client.get_object(Bucket=bucket_name, Key=object_key)['Body']
    if not hasattr(body, "__iter__"): 
        body.__iter__ = types.MethodType(__iter__, body)
    
    llm_data = pd.read_csv(body)
    llm_data = llm_data.replace([np.inf, -np.inf], np.nan)  # Replace inf with NaN
    llm_data = llm_data.fillna(0)

    print(llm_data.head(10))
    
    access_token=get_access_token()

#    # Store LLM data as payload
#     payload_data_set_id = store_llm_data_as_payload(subscription_id, llm_data)
#     print(f"Payload Data Set ID: {payload_data_set_id}")

    # Store LLM data as feedback
    feedback_dataset_id = store_llm_data_as_feedback(subscription_id, llm_data, access_token, data_mart_id, openscale_api_url)


#Call function for the process
process_and_store_llm_data(bucket_name, SUBSCRIPTION_ID, data_mart_id, OPENSCALE_API_URL)
