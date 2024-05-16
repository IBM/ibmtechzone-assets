from ibm_cloud_sdk_core.authenticators import IAMAuthenticator,BearerTokenAuthenticator
from typing import List
from pydantic import BaseModel
from ibm_watson_openscale import *
from ibm_watson_openscale.supporting_classes.enums import *
from ibm_watson_openscale.supporting_classes import *

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

import requests
import warnings
import pandas as pd
import json
import os

from dotenv import load_dotenv
import nest_asyncio
nest_asyncio.apply()


load_dotenv()
api_key = os.getenv("WATSONX_APIKEY", None)
# ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
project_id = os.getenv("IBM_CLOUD_PROJECT", None)

credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": api_key,
}

authenticator = IAMAuthenticator(apikey=credentials.get("apikey"))
client = APIClient(authenticator=authenticator)

from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings()


from ibm_metrics_plugin.common.utils.constants import ExplainabilityMetricType
from ibm_metrics_plugin.metrics.explainability.entity.explain_config import ExplainConfig
from ibm_metrics_plugin.common.utils.constants import InputDataType,ProblemType

authenticator = IAMAuthenticator(apikey=credentials.get("apikey"))
client = APIClient(authenticator=authenticator)

# from langchain.embeddings import HuggingFaceEmbeddings

# embeddings = HuggingFaceEmbeddings()

config_json = {
            "configuration": {
                "input_data_type": InputDataType.TEXT.value,
                "problem_type": ProblemType.QA.value,
                "feature_columns":["context"],
                "prediction": "generated_text", #Column name that has the prompt response from FM
                "context_column": "context",
                "explainability": {
                    "metrics_configuration":{
                        ExplainabilityMetricType.PROTODASH.value:{
                                    "embedding_fn": embeddings.embed_documents #Make sure to supply the embedded function else TfIDfvectorizer will be used
                                }
                    }
                }
            }
        }

app = FastAPI()

@app.post("/ask")
async def ask_question(question: dict):
    user_query = question.get('question')
    if not user_query:
        raise HTTPException(status_code=400, detail="Question not provided")
    print("***********question", user_query)
    resp = get_response(user_query)
    if isinstance(resp, str) or 'table' not in resp:
        raise HTTPException(status_code=500, detail=f"Unexpected response format: {resp}")
    
    formatted_products = format_product_info(resp['table'])
    print("************ formatted_products", formatted_products)
    generated_text = resp.get('response')
    if not generated_text:
        raise HTTPException(status_code=500, detail="Generated text not found in response")
    print("************ generated_text", generated_text)
    results = protodash_resp(generated_text, formatted_products)
    print("************ results", results)
    return {"results": results, "generated_text":generated_text, "table":resp['table']}

def get_response(question):
    url = 'https://tanishq-deployment.1gplwvooup58.us-south.codeengine.appdomain.cloud/ask'
    headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
    data = {'question': question}
    response = requests.post(url, json=data, headers=headers)
    print("response",response)
    # print(f"Response Status Code: {response.status_code}")
    # print(f"Response Content: {response.text}")
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        return f"Invalid JSON response: {response.text}"

    return response_json if response.status_code == 200 else f"Error: {response.status_code}"

def format_product_info(products):
    product_strings = []
    for product in products:
        product_string = ", ".join(f"{key}: {value}" for key, value in product.items())
        product_strings.append(product_string)
    return product_strings

def protodash_resp(generated_text, formatted_products):
    temp = {"generated_text": generated_text, "context": formatted_products}
    data = pd.DataFrame([temp])
    warnings.filterwarnings("ignore")
    results = client.ai_metrics.compute_metrics(configuration=config_json, data_frame=data)
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
