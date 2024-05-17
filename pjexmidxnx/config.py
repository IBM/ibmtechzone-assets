from dotenv import load_dotenv
import os
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods

load_dotenv()
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
watson_ai_project_id = os.getenv("PROJECT_ID", None)
watson_ai_api_key = os.getenv("API_KEY", None)

watsonx_selenium_object_config = {
    "genAI_config": {
        "model_id":"codellama/codellama-34b-instruct-hf",
        "api_key": watson_ai_api_key,
        "url": "https://us-south.ml.cloud.ibm.com",
        "project_id": watson_ai_project_id,# need to make project in watsonx.ai
        "decoding_method": DecodingMethods.SAMPLE, 
        "min_tokens": 1,
        "max_tokens": 4000,
        "temperature": 0.6,
        "repetition_penalty":1,
        "stop_sequences": [],
    }
}

watsonx_selenium_object_config_greedy = {
    "genAI_config": {
        "model_id":"codellama/codellama-34b-instruct-hf",
        "api_key": watson_ai_api_key,
        "url": "https://us-south.ml.cloud.ibm.com",
        "project_id": watson_ai_project_id,# need to make project in watsonx.ai
        "decoding_method": DecodingMethods.GREEDY, 
        "min_tokens": 1,
        "max_tokens": 4000,
        "temperature": 0.6,
        "repetition_penalty":1,
        "stop_sequences": ["\n\nNote:","Note:", "Input:", '↵↵', 'Explanation:'],
    }
}

# API_KEY=BELum2c4YKgFmrlpGFEXQGlVklxrhLkt-F-M68n3IInT
# IBM_CLOUD_URL=https://us-south.ml.cloud.ibm.com
# PROJECT_ID=7a31a166-4a8a-4bb2-a145-88e0d537deb2