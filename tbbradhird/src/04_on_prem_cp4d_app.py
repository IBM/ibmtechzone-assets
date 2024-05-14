import json
import os
import time
from typing import List

import pandas as pd
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Response, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel



from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate



# from rbi_shortlist_resumes import shortlist_for_given_job
from utils import file_folder_operations

##### chat

from watson_CE_modules import watson_discovery

from utils import pdf_loader
from utils import text_splitter



app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
user_name = os.getenv("USERNAME", None)
api_key_env = os.getenv("WATSONX_APIKEY", None)
wx_project_id = os.getenv("WX_PROJECT_ID", None)


##(username/apikey):
wml_credentials = {
    "url": ibm_cloud_url,
    "username": user_name,
    "apikey": api_key_env,
    "instance_id": "openshift"  #TBD: Only enable for CP4D deployment
}



@app.get('/')
def rbi_hr_server_root():
    return Response(content='On-prem APP server root', status_code=status.HTTP_200_OK)


@app.get('/test/')
def test():
    return Response(content='test response', status_code=status.HTTP_200_OK)


# Get the IP & PORT from environment
ip_address = os.getenv('IP_ADDRESS', '0.0.0.0')
port = os.getenv('PORT', 8000)
timeout_seconds = 360 #6min timeout
if __name__ == "__main__":
    uvicorn.run(app, host=ip_address, port=port, timeout_keep_alive=timeout_seconds)
