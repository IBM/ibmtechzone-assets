#Importing libraries
import xml.etree.ElementTree as ET
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning import APIClient
from dotenv import load_dotenv
import re
import requests, json
import pandas as pd
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

def get_inst_for_query_gen(xml_components, inst1, endpoint_url, bearer_token):
    # Prepare the JSON payload
    xml_components = '''Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation.
    The generated text should give source name, destination name, and transformation applied on each columns.
    Mention the appropriate transformation on columns using information available in destination.''' + xml_components + "</instructions>"

    inst1 = "<instructions>" + inst1
    payload = {
        "parameters": {
            "prompt_variables": {   "xml_content": inst1,
                                    "inst1": xml_components
                                    
                                }
        }
    }
    # print("*"*50)
    # print("payload::")
    # print(payload)
    # print(type(payload))
    # print("*"*50)

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

def get_sql_query_for_inst(instructions, inst2, endpoint_url, bearer_token):
    # Prepare the JSON payload
    instructions = instructions + "Generate sql query only" + "strongly start sql query with ```(triple ticks) and end it with ``` (triple ticks) \n </instructions>"

    inst2 = "<instructions> \n " + inst2
    payload = {
        "parameters": {
            "prompt_variables": {   "inst2": inst2,  # csv inst2
                                    "generated_instructions": instructions  # output of model1
                                    
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
def get_mapping_tag_names(xml_path):
    """
    Function to get the list of mapping tag names available in the XML file.
    
    Args:
    - xml_path: Path to the XML file
    
    Returns:
    - List of mapping tag names
    """
    mapping_tag_names = []
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for mapping in root.findall('.//MAPPING'):
            mapping_tag_names.append(mapping.attrib['NAME'])
    except FileNotFoundError:
        print("File not found at:", xml_path)
    except Exception as e:
        print("An error occurred:", e)
    return mapping_tag_names

def list_transformation_names(xml_path, mapping_name):
    """
    Function to get the list of transformation names within the specified mapping tag.
    
    Args:
    - xml_path: Path to the XML file
    - mapping_name: Name of the mapping tag
    
    Returns:
    - List of transformation names within the specified mapping tag
    """
    transformation_names = []
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Find the specified mapping tag
        mapping = root.find(".//MAPPING[@NAME='{}']".format(mapping_name))
        if mapping is not None:
            # Collect transformation names within the mapping tag
            for transformation in mapping.findall(".//TRANSFORMATION"):
                transformation_name = transformation.get('NAME')
                if transformation_name:
                    transformation_names.append(transformation_name)
    except FileNotFoundError:
        print("File not found at:", xml_path)
    except Exception as e:
        print("An error occurred:", e)
    
    return transformation_names

# def list_transformation_names(xml_file):
#     tree = ET.parse(xml_file)
#     root = tree.getroot()
#     transformation_names = []
#     for elem in root.iter('TRANSFORMATION'):
#         if 'NAME' in elem.attrib:
#             transformation_names.append(elem.attrib['NAME'])
#     return transformation_names

def get_unique_from_instances_by_to_instance(xml_path, mapping_name, to_instance):
    """
    Function to create a dictionary where each unique 'TOINSTANCE' name is associated with a list of unique 'FROMINSTANCE' names
    of the connector tags within the selected mapping tag based on the inputted 'to_instance'.
    
    Args:
    - xml_path: Path to the XML file
    - mapping_name: Name of the mapping tag
    - to_instance: Name of the 'to_instance' to filter the results
    
    Returns:
    - Dictionary where keys are unique 'TOINSTANCE' names and values are lists of unique 'FROMINSTANCE' names
    """
    from_instances_by_to_instance = {}
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        mapping = root.find(".//MAPPING[@NAME='{}']".format(mapping_name))
        if mapping is not None:
            for connector in mapping.findall('.//CONNECTOR[@TOINSTANCE="{}"]'.format(to_instance)):
                to_instance = connector.get('TOINSTANCE')
                from_instance = connector.get('FROMINSTANCE')
                if to_instance:
                    if to_instance not in from_instances_by_to_instance:
                        from_instances_by_to_instance[to_instance] = set()  # Using set to store unique values
                    from_instances_by_to_instance[to_instance].add(from_instance)
    except FileNotFoundError:
        print("File not found at:", xml_path)
    except Exception as e:
        print("An error occurred:", e)
    
    # Convert sets to lists
    for to_instance, from_instances_set in from_instances_by_to_instance.items():
        from_instances_by_to_instance[to_instance] = list(from_instances_set)
    
    return from_instances_by_to_instance

def collect_transformations_and_connectors(xml_path, to_instance_name, from_instance_names):
    """
    Function to collect transformations and connector tags based on the provided to_instance and from_instance names.
    
    Args:
    - xml_path: Path to the XML file
    - to_instance_name: Name of the 'to_instance'
    - from_instance_names: List of names of the 'from_instance'
    
    Returns:
    - Tuple containing:
      - List of transformation names between 'to_instance_name' and 'from_instance_names'
      - List of connector tags whose 'to_instance' is the same as 'to_instance_name'
    """
    transformations = []
    connectors = []
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Collect transformations between 'to_instance_name' and any of the 'from_instance_names'
        transformation_names = set([to_instance_name] + from_instance_names)
        print("transformation_names::", transformation_names)
        for transformation in root.findall(".//TRANSFORMATION"):
            transformation_name = transformation.get('NAME')
            if transformation_name in transformation_names:
                transformations.append(ET.tostring(transformation, encoding='unicode'))
        
        # Collect connector tags whose 'to_instance' is the same as 'to_instance_name'
        for connector in root.findall(".//CONNECTOR[@TOINSTANCE='{}']".format(to_instance_name)):
            connectors.append(ET.tostring(connector, encoding='unicode'))
    
    except FileNotFoundError:
        print("File not found at:", xml_path)
    except Exception as e:
        print("An error occurred:", e)
    
    return transformations, connectors


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





def read_mapping_xls(transformation_name, xls_file):
    # Read Excel file into a pandas DataFrame
    df = pd.read_excel(xls_file, header=1)  # Assuming the header is in the first row
    print("columns::", df.columns)
    
    # Set 'transformation_name' column as index
    df.set_index('transformation_name', inplace=True)
    
    # Convert DataFrame to dictionary
    content_file_dict = df.to_dict(orient='index')

    if transformation_name in content_file_dict:
        # Fetch and return the XML content for the provided transformation name
        xml_content = content_file_dict[transformation_name]['xml_content']
        inst1 = content_file_dict[transformation_name]['instructions_to_model1']
        inst2 = content_file_dict[transformation_name]['instructions_to_model2']
        return xml_content,inst1,inst2
    else:
        return "No Transformation found", "No Transformation found", "No Transformation found"

