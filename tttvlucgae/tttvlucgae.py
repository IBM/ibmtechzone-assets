# Install required libraries
import os
import json
import wget
from copy import deepcopy
import pandas as pd
import plotly.graph_objects as go
from langchain.embeddings import HuggingFaceEmbeddings
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_metrics_plugin.common.utils.constants import ExplainabilityMetricType
from ibm_metrics_plugin.metrics.explainability.entity.explain_config import ExplainConfig
from ibm_metrics_plugin.common.utils.constants import InputDataType,ProblemType
from ibm_watson_openscale import APIClient as WOSClient
from ibm_watson_openscale.supporting_classes.enums import *
from ibm_watson_openscale.supporting_classes import *


# Setup credentials
WATSONX_API_KEY = os.environ["watsonx_api_key"]


# Download sample data
filename = "sample_cricket_data.csv"
url = "https://raw.githubusercontent.com/gautamgc17/RAG-Assets/main/sample_data/sample_cricket_data.csv"
if not os.path.isfile(filename):
    wget.download(url, out=filename)
    print(f"Downloaded File - {filename}")
else:
    print("File with same name already exists! Skipping download....")


# Read data
df = pd.read_csv(os.path.abspath("sample_cricket_data.csv"))
data = deepcopy(df)
data = data.rename(columns={'Answer': 'generated_text'})
data['context'] = data[['Chunk1', 'Chunk2', 'Chunk3']].apply(list, axis=1)
data = data.drop(columns=['Question', 'Chunk1', 'Chunk2', 'Chunk3'])
print("DataFrame Shape:\n", data.shape)
print("Data Columns:\n", data.columns)


# Download embeddings
embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')


# Initialize the OpenScale Client
authenticator = IAMAuthenticator(apikey = WATSONX_API_KEY)
client = WOSClient(authenticator = authenticator)
print("Successfully Initialized the Client!!")


# Define the configuration for ProtoDash
config_json = {
    "configuration": {

        "input_data_type": InputDataType.TEXT.value,
        "problem_type": ProblemType.QA.value,
        "feature_columns":["context"],
        "prediction": "generated_text",   # Column name that has the prompt response from LLM
        "context_column": "context",
        "explainability": {

            "metrics_configuration": {
                ExplainabilityMetricType.PROTODASH.value:{
                    "embedding_fn": embeddings.embed_documents   # Provide the embedded function else TfIDfvectorizer will be used
                }
            }
        }
    }
}


# Compute metrics 
results_response = client.ai_metrics.compute_metrics(configuration=config_json,data_frame=data)
metrics = results_response.get("metrics_result")
results = metrics.get("explainability").get("protodash")
print("Results:\n", results)


# Plot graph for visualization
output_dir = "protodash_plots"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

protodash_data = metrics['explainability']['protodash']

for idx, (question, entry) in enumerate(zip(df["Question"].tolist(), protodash_data), start=1):
    prototypes = entry['prototypes']['values']
    weights = [prototype[0] for prototype in prototypes]
    contexts = [prototype[1] for prototype in prototypes]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=[f'Context {i+1}' for i in range(len(contexts))],
        x=weights,
        orientation='h',
        marker=dict(color='skyblue'),
        hovertext=contexts,  
        hoverinfo='text',
        hovertemplate='%{hovertext}<extra></extra>',  
    ))

    fig.update_layout(
        title=f'ProtoDash Results (Question {idx})',
        xaxis_title='Source Attribution (Weight)',
        yaxis_title='Source Document',
        height=600,
        margin=dict(l=100, r=50, t=75, b=50),
        showlegend=False,
    )

    fig.update_traces(hoverlabel=dict(bgcolor='rgba(255,255,255,0.7)', font_size=13))

    # Show the plot
    fig.show()

    # Save the plot as an image file
    image_file = os.path.join(output_dir, f'protodash_result_question_{idx}.png')
    fig.write_image(image_file)
    
    print(f'Saved plot for Question {idx} to {image_file}')
    