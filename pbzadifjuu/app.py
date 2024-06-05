import os
import pandas as pd
import streamlit as st
from streamlit import session_state
import xml.etree.ElementTree as ET
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
from dotenv import load_dotenv
load_dotenv()
# Function to handle XML file parsing and transformation
import streamlit as st
from streamlit import runtime
import sys
from streamlit.web import cli as stcli
from test import *
#--------------------------------------------------------------------------------------------------------------------------

# defining variables

PROJECT_ID =sys.argv[1]
# print("PROJECT_ID::", PROJECT_ID)
IBM_CLOUD_URL = sys.argv[2]
API_KEY = sys.argv[3]
IAM_URL = sys.argv[4]
SPACE_ID = sys.argv[5]
ENDPOINT_URL1 = sys.argv[6]
ENDPOINT_URL2 = sys.argv[7]


creds = {
    "url": IBM_CLOUD_URL,
    "apikey": API_KEY
}
project_id = PROJECT_ID


# model_name = "ibm-mistralai/mixtral-8x7b-instruct-v01-q"
model_name = "mistralai/mixtral-8x7b-instruct-v01"
model_params = {
        "decoding_method": "greedy",
        "max_new_tokens": 3000,
        "min_new_tokens": 10,
        "stop_sequences": [],   
        "repetition_penalty": 1
    }


print("IBM_CLOUD_URL:", IBM_CLOUD_URL)
# Instantiate a model proxy object to send your requests
model = Model(
    model_id=model_name,
    params=model_params,
    credentials=creds,
    project_id=project_id
    )

# --------------------------------------------------------------------------------

CLOUD_API_KEY = API_KEY
IAM_URL = IAM_URL
WML_CREDENTIALS = {
                   "url": IBM_CLOUD_URL,
                   "apikey": CLOUD_API_KEY
}


wml_client = APIClient(WML_CREDENTIALS)
project_id = PROJECT_ID
existing_space_id = SPACE_ID
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
    
import getpass
import os
from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models import ModelInference

credentials = {
    "url": IBM_CLOUD_URL,
    "apikey": API_KEY
}


project_id = PROJECT_ID



model_id = "ibm-mistralai/mixtral-8x7b-instruct-v01-q"



parameters = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MAX_NEW_TOKENS: 800,
    GenParams.STOP_SEQUENCES: ["<end·of·code>"]
}


model = ModelInference(
    model_id=model_id, 
    params=parameters, 
    credentials=credentials,
    project_id=project_id)




def get_result(text):
    text = '<instructions> \n' + text + ' \n </instructions>'
    # print("TEXT:::", text)
    response = model.generate_text(text)
    return response
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




#--------------------------------------------------------------------------------------------------------------------------
class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def process_xml_file(xml_file_path):

    mapping_names = get_mapping_tag_names(xml_file_path)
    selected_mapping_name = st.selectbox("Select Mapping", mapping_names)

    # Get transformation names
    transformation_names = list_transformation_names(xml_file_path, selected_mapping_name)
    
    # Display transformation names as select options
    selected_transformation = st.selectbox("Select Transformation", transformation_names)
    
    # Initialize session state
    if 'submit_clicked' not in st.session_state:
        st.session_state.submit_clicked = False
        st.session_state.generate_sql_clicked = False
    
    # Button to submit
    if not st.session_state.submit_clicked:
        if st.button("Submit"):
            st.session_state.submit_clicked = True
            
    if st.session_state.submit_clicked:
        # Trigger get_elements_by_attribute_value with selected value
        # matching_elements = get_elements_by_attribute_value(xml_file_path, selected_transformation)
        # matching_elements = get_unique_from_instances_by_to_instance(xml_file_path, selected_mapping_name, selected_transformation)
        # if len(matching_elements) >0:
        #     to_instance_name = next(iter(matching_elements))
        #     from_instance_names = matching_elements[to_instance_name]

        # # Extract text content from XML elements
        # transformations, connectors = collect_transformations_and_connectors(xml_file_path, to_instance_name, from_instance_names)

        # matching_texts = "".join((transformations+connectors))
        # Display matching elements in a scrollable window
        xls_file = "llm_inputs_for_ui 2.xls"
        xml_content,inst1,inst2 = read_mapping_xls(selected_transformation, xls_file)
        # inst2 = inst2+"Generate sql query only"
        matching_texts = xml_content

        st.text_area("Matching Elements", matching_texts, height=200)
        # st.text_area("prompt1", xml_content + inst1, height=500)
        

        # st.markdown(
        #             f'<style>.scrollable-code .st-cm {{ max-height: 300px; overflow-y: scroll; }}</style>',
        #             unsafe_allow_html=True
        #         )
        # st.code(txt_matching_texts, language='xml')
        
        # Button to generate SQL query
        if not st.session_state.generate_sql_clicked:
            if st.button("Generate SQL Query"):
                # Send prompt to WatsonXAI and display response
                iam_access_token = generate_access_token(API_KEY, IAM_URL)

                # response = get_sql_query(matching_texts, ENDPOINT_URL1"), iam_access_token)
                # response1 = get_inst_for_query_gen(matching_texts, inst1, ENDPOINT_URL1"), iam_access_token)
                response1 = get_result(inst1 +''' \n Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation.
    The generated text should give source name, destination name, and transformation applied on each columns.
    Mention the appropriate transformation on columns using information available in destination. \n'''+" " + matching_texts)
                # instructions = response1.json()['results'][0]['generated_text']
                instructions = "Fetch "+response1.split("Fetch")[-1]
                
                # st.text_area("prompt2", inst2 + instructions, height=500)
                # st.write("Instructions for SQL Query Generation \n __________________________________________")
                # st.write(response1)
                response = get_sql_query_for_inst(instructions, inst2, ENDPOINT_URL2, iam_access_token)
                response = response.json()['results'][0]['generated_text']
                # response1 = extract_text_between_backticks(response)
                st.write("SQL Query Generated \n __________________________________________")
                st.write(response)
                # st.code(response1, language='sql')
                # st.session_state.generate_sql_clicked = True


# Main Streamlit app
def main():
    st.title("XML to SQL Query Generator")
    
    # File upload
    uploaded_file = st.file_uploader("Upload XML File", type=["xml"])
    
    if uploaded_file is not None:
        # Save uploaded file to current working directory
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Display uploaded file name
        st.write(f"Uploaded XML file: {uploaded_file.name}")
        
        # Process XML file
        process_xml_file(file_path)
    
if __name__ == "__main__":
    main()
