from dotenv import load_dotenv
import os
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods

load_dotenv()
watson_ai_project_id = os.environ["watson_ai_project_id"]
watson_ai_api_key = os.environ["watson_ai_api_key"]

watsonx_pdf_summarization_config = {
    "genAI_config": {
        "model_id":"mistralai/mixtral-8x7b-instruct-v01",
        "api_key": watson_ai_api_key,
        "url": "https://us-south.ml.cloud.ibm.com",
        "project_id": watson_ai_project_id,# need to make project in watsonx.ai
        "decoding_method": DecodingMethods.GREEDY, 
        "min_tokens": 10,
        "max_tokens": 1500,
        "temperature": 0.10,
        "repetition_penalty":1.20,
        "stop_sequences": [],
    }
}