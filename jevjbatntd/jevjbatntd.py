import gradio as gr  # Gradio is used for creating the web interface
import requests  # Requests is used for making HTTP requests
import os  # OS module is used for interacting with the operating system
import time  # Time module is used for time-related functions
from langchain.embeddings import HuggingFaceEmbeddings  # Import HuggingFaceEmbeddings from langchain
from langchain.document_loaders import TextLoader  # Import TextLoader from langchain
from langchain.document_loaders.base import BaseLoader  # Base class for document loaders
from langchain_core.documents import Document  # Import Document class from langchain core
from ibm_botocore.client import Config as BotoConfig  # IBM Botocore Config for client configuration
from ibm_botocore.client import ClientError  # IBM Botocore ClientError for error handling

#Login Credentials : ID="User",Password="Password@1234"
ID = input("Enter User ID: ")  # Input Id
Password = input("Enter User Password: ")   # Input Password
Wx_Api_Key = input("Enter your API_Key_value: ")  # Input Wx API Key
Project_ID = input("Enter Project_ID: ")  # Input Project ID

def sum_text(input_text, lang="out"):
    """
    Summarize the input text using a specified language model.
    :param input_text: The text to be summarized
    :param lang: Language setting for summarization instructions
    :return: Summarized text
    """
    global bearer_token, token_expiry_time
    # Refresh the bearer token if it has expired
    if time.time() > token_expiry_time:
        bearer_token = get_bearer_token()
        token_expiry_time = time.time() + 3600

    # Set the instruction based on the language parameter
    if lang == "out":
        instruction = "Summarize the following input clearly and concisely"
    else:
        instruction = """
        Please summarize the following text clearly and concisely.
        """

    # Define the API endpoint and headers for the request
    url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + bearer_token,
    }

    # Define the data payload for the request
    data = {
        "model_id": "meta-llama/llama-3-70b-instruct",
        "project_id": Project_ID,
        "parameters": {
            "decoding_method": "greedy",
            "min_new_tokens": 1,
            "max_new_tokens": 2000
        },
        "prompt_id": "prompt_builder",
        "input": instruction + "\n\n" + "Input: " + input_text + "\n\n" + "Output: ",
    }

    # Send the request to the API and retrieve the response
    response = requests.post(url, headers=headers, json=data)
    response_final = response.json()["results"][0]["generated_text"]
    return response_final  # Return the summarized text

# Function to get the bearer token for authentication
def get_bearer_token():
    """
    Get the bearer token for authentication.
    :return: Bearer token
    """
    token_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {
        "apikey": Wx_Api_Key,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    }
    response = requests.post(token_url, headers=headers, data=data)
    token = response.json()["access_token"]
    return token  # Return the bearer token

# Initialize bearer token and expiry time
bearer_token = get_bearer_token()
token_expiry_time = time.time() + 3600

# Ensure all your imports and setup are correctly configured, especially the imports related to your COSClient

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("Sales AI Assistant")  # Add a markdown title

    with gr.Tab("Summarization Engine"):  # Create a tab for the summarization engine
        with gr.Row():  # Create a row for input and button
            input_text = gr.Textbox(label="Input Text")  # Textbox for input text
            summary_button = gr.Button("Submit")  # Button to submit the text
            response_final = gr.Textbox(label="Summarized text")  # Textbox to display summarized text

    # Define the click action for the submit button
    summary_button.click(sum_text, inputs=[input_text], outputs=[response_final])

    demo.queue()  # Add the demo to the Gradio queue
    if ID is None:  # Local deployment
        demo.launch(show_api=False, server_name="0.0.0.0", server_port=8080,share=True)
    else:  # Production deployment
        demo.launch(auth=(ID, Password), show_api=False, server_name="0.0.0.0")
