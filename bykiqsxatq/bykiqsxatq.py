# Import required libraries
import os
import json
import requests
import subprocess
import pandas as pd  
from datetime import datetime 
from ibm_watson_machine_learning import APIClient
from ibm_watson_machine_learning.helpers import DataConnection
from ibm_watson_machine_learning.experiment import TuneExperiment
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models import ModelInference


# Define credentials
WATSONX_API_KEY = os.environ["watsonx_api_key"]
IBM_CLOUD_URL = os.environ["ibm_cloud_url"]
PROJECT_ID = os.environ["project_id"]
credentials = {"url": IBM_CLOUD_URL, "apikey": WATSONX_API_KEY}


# Set up client - Create an instance of APIClient with authentication details.
client = APIClient(credentials)
client.set.default_project(PROJECT_ID)
print("Connection to watsonx set up succesfully")


# Load the sample data from Huggingface for Summarization Task
url = "https://huggingface.co/api/datasets/therapara/summary-of-news-articles/parquet/default/train"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: Unable to fetch data. Status code: {response.status_code}")
    

# Download the data
output_file = "sample_data.parquet"
subprocess.run(['wget', '-O', output_file, data[0]], check=True)


# Convert the Parquet file to JSON format
json_file = 'sample_data.json'
df = pd.read_parquet(os.path.abspath("sample_data.parquet"))
df.rename(columns={'document': 'input', 'summary': 'output'}, inplace=True)
print("Original Data Shape:", df.shape)
filtered_data = df.sample(n = 1000, random_state = 42).reset_index(drop=True)
print("Filtered Data Shape:", filtered_data.shape)
filtered_data.to_json(json_file, orient='records')
print(f"Parquet file converted to JSON and saved as {json_file}.")


# Load the local training data
tuning_filepath = os.path.abspath(json_file)


# Set the name for your data you will load to the project
tuning_file_name = 'article_summarization_data.json'
asset_details = client.data_assets.create(name=tuning_file_name, file_path=tuning_filepath)


# Define connection information to training data
asset_id = client.data_assets.get_id(asset_details)
data_conn = DataConnection(data_asset_id=asset_id)


# Initialize the experiment
experiment = TuneExperiment(credentials, project_id=PROJECT_ID)
print("All available tasks:\n", {task.name: task.value for task in experiment.Tasks})


# Define parameters for prompt_tuner  
# For more details, refer - https://ibm.github.io/watson-machine-learning-sdk/tune_experiment.html#ibm_watson_machine_learning.experiment.fm_tune.TuneExperiment.prompt_tuner
prompt_tuner = experiment.prompt_tuner(
    name="Prompt Tuning - News Article Summarization Task",
    task_id=experiment.Tasks.SUMMARIZATION,
    base_model='google/flan-t5-xl',
    accumulate_steps=32,
    batch_size=16,
    learning_rate=0.2,
    max_input_tokens=256,
    max_output_tokens=50,
    num_epochs=5,
    tuning_type=experiment.PromptTuningTypes.PT,
    verbalizer="Summarize the input article. Input: {{input}} Output: ",
    auto_update_model=True
)
print("Configuration parameters of PromptTuner\n", prompt_tuner.get_params())


# Run prompt tuning process of foundation model
tuning_details = prompt_tuner.run(training_data_references=[data_conn], background_mode=False)
print("Status/State of initialized Prompt Tuning run\n", prompt_tuner.get_run_status())
print("Prompt Tuning run details:\n", prompt_tuner.get_run_details())


# Create a deployment for the model
model_id = None
if 'model_id' in tuning_details.get('entity', {}):
    model_id = tuning_details['entity']['model_id']
meta_props = {
    client.deployments.ConfigurationMetaNames.NAME: "Summarization Task Prompt Tuning Deployment",
    client.deployments.ConfigurationMetaNames.ONLINE: {},
    client.deployments.ConfigurationMetaNames.SERVING_NAME : f"pt_sdk_deployment_{datetime.utcnow().strftime('%Y_%m_%d_%H%M%S')}"
}
deployment_details = client.deployments.create(model_id, meta_props)
assert deployment_details["entity"]["status"]["state"].lower() == "ready"
deployment_id = deployment_details['metadata']['id']


# Perform Inference over tuned model
generate_params = {
    GenParams.MAX_NEW_TOKENS: 100,
    GenParams.MIN_NEW_TOKENS: 10,
    GenParams.DECODING_METHOD: 'greedy',
    GenParams.REPETITION_PENALTY: 1.5
}
tuned_model = ModelInference(
    deployment_id=deployment_id,
    params=generate_params,
    api_client=client
)
print("Model Inference Details:\n", tuned_model.get_details())


# Get a response for a sample note
print("Getting a response for a sample article....\n")

prompt = """
Summarize the following input news article
Input: 
Amazon facing 'real-life Avatar' says James Cameron James Cameron, the director, has said a real-life "Avatar" battle is playing out in Brazil's Amazon rain forest, where indigenous groups are trying to halt the construction of a huge hydroelectric project. 
'Avatar' director James Cameron and actress Sigourney Weaver were in Sao Paulo on Sunday to promote the DVD and Blu-Ray release of his film, which earlier this year became the highest-grossing movie of all time. (April 11).
Output:
"""

response = tuned_model.generate(prompt=prompt)
print("GENERATED SUMMARY:", response["results"][0]["generated_text"].strip())
print("INPUT TEXT TOKEN COUNT:", response["results"][0]["input_token_count"])
print("GENERATED TEXT TOKEN COUNT:", response["results"][0]["generated_token_count"])