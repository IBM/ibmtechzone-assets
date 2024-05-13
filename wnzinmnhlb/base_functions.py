#Importing libraries
import xml.etree.ElementTree as ET
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning import APIClient
from dotenv import load_dotenv
import re
import requests, json
# Load variables from .env file
load_dotenv()
import os

#defining variables
creds = {
    "url": os.getenv("IBM_CLOUD_URL"),
    "apikey": os.getenv("API_KEY")
}
project_id = os.getenv("PROJECT_ID")


# model_name = "ibm-mistralai/mixtral-8x7b-instruct-v01-q"
model_name = "mistralai/mixtral-8x7b-instruct-v01"
model_params = {
        "decoding_method": "greedy",
        "max_new_tokens": 3000,
        "min_new_tokens": 10,
        "stop_sequences": [],
        "repetition_penalty": 1
    }



# Instantiate a model proxy object to send your requests
model = Model(
    model_id=model_name,
    params=model_params,
    credentials=creds,
    project_id=project_id
    )

# --------------------------------------------------------------------------------

CLOUD_API_KEY = os.getenv("API_KEY")
IAM_URL = os.getenv("IAM_URL")
WML_CREDENTIALS = {
                   "url": os.getenv("IBM_CLOUD_URL"),
                   "apikey": CLOUD_API_KEY
}


wml_client = APIClient(WML_CREDENTIALS)
project_id = os.getenv("PROJECT_ID")
existing_space_id = os.getenv("SPACE_ID")
use_existing_space = True

def generate_access_token(CLOUD_API_KEY, IAM_URL):
    headers={}
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Accept"] = "application/json"
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": CLOUD_API_KEY,
        "response_type": "cloud_iam"
    }
    response = requests.post(IAM_URL, data=data, headers=headers)
    json_data = response.json()
    iam_access_token = json_data['access_token']
    return iam_access_token


def get_sql_query(xml_components, endpoint_url, bearer_token):
    # Prepare the JSON payload
    payload = {
        "parameters": {
            "prompt_variables": {
                                    "xml_file_components": xml_components
                                }
        }
    }

    # Prepare the headers with the bearer token
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    try:
        # Send POST request to the API endpoint with headers
        response = requests.post(endpoint_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

#         # Parse the JSON response
#         result = response.json()

#         # Extract the SQL query from the response
#         sql_query = result.get("sql_query", "No SQL query found")

        return response

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None




# --------------------------------------------------------------------------------


def list_transformation_names(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    transformation_names = []
    for elem in root.iter('TRANSFORMATION'):
        if 'NAME' in elem.attrib:
            transformation_names.append(elem.attrib['NAME'])
    return transformation_names

def get_elements_by_attribute_value(xml_file, value):
    element_list=[]
    tree = ET.parse(xml_file)
    root = tree.getroot()
    matching_elements = []
    for elem in root.iter():
        for attr_name, attr_value in elem.attrib.items():
            if attr_value == value:
                matching_elements.append(elem)
                break  # Break the inner loop as soon as a match is found
    return matching_elements


def build_prompt(prompt, matching_elements):
    return prompt.format(matching_elements)




def get_response(txt_matching_texts):
    prompt = '''sytem role:: you are an expert in understanding xml files used to design etl pipelines for informatica and convert them to sql queries
    Here are the elements of an transformation gathered:
    {txt_matching_texts}
    
    below are the instructions to follow while generating sql queries based on the xml elements provided:
    1. do not miss any information of the elements provided in xml file
    2. do not repeat or add extra text in the response
    3. consider every single information availabel in the elements provided from xml file. 
    4. Very strong instruction: start the sql query with ```(triple ticks) and end with ```(triple ticks)

    query: generate an sql query based on the elements of an transformation provided
    Sql query: 

    '''

    response = model.generate_text(prompt)
    return response



def extract_text_between_backticks(text):
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

