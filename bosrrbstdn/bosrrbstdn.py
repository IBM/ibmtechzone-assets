import requests
from dotenv import load_dotenv
import json
import os
load_dotenv(".env")

api_key = os.getenv("IBM_API_KEY", None)
ibm_cloud_url =os.getenv("IBM_CLOUD_URL", None)
project_id = os.getenv("PROJECT_ID", None)


data = {
    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    "apikey": api_key
}
res = requests.post("https://iam.cloud.ibm.com/identity/token",data = data, headers={"Content-Type": "application/x-www-form-urlencoded","Accept":"application/json"})
res = res.json()

prompt="""Your example prompt goes here"""

token_data = json.dumps({
  "model_id": "meta-llama/llama-3-70b-instruct",
  "input": prompt,
  "parameters": {
    "return_tokens": False
  },
  "project_id": project_id
})

headers = {
    "Accept":"application/json",
    "Authorization":"Bearer "+res["access_token"],
    "Content-Type":"application/json"
}

res = requests.post(f"{ibm_cloud_url}/ml/v1/text/tokenization?version=2023-05-02",data = token_data, headers=headers)

res = res.json()
print("Number of token in prompt:- ",res["result"]["token_count"])