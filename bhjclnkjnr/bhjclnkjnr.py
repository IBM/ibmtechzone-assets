from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ibm_watson_machine_learning.foundation_models import Model

import re
import json

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# Parameters for WatsonxLLM model
parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 2000,
    "min_new_tokens": 1,
}

# Retrieve credentials and configurations from environment variables
api_key = os.getenv("api_key", None)
cloud_url = os.getenv("cloud_url", "https://us-south.ml.cloud.ibm.com")
project_id = os.getenv("project_id", None)

# Initialize WatsonxLLM with the specified model, credentials, and parameters
watsonx_llm = Model(
    model_id="meta-llama/llama-3-70b-instruct",
    credentials={"url": cloud_url, "apikey": api_key},
    project_id=project_id,
    params=parameters,
)


def extract_json(text):
    """
    Extracts JSON string from the given text using regular expression.

    Args:
    text (str): Input text containing JSON.

    Returns:
    str: Extracted JSON string.
    """
    pattern = r"\{([\s\S]*)\}"
    matches = re.findall(pattern, text)
    return "{" + matches[0] + "}"


def json_parser(llm_response):
    """
    Parses the JSON string from the LLM response and handles any JSON errors.

    Args:
    llm_response (str): Response text from the LLM containing JSON.

    Returns:
    dict: Parsed JSON object.
    """
    json_text = extract_json(llm_response)
    try:
        json_obj = json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        print("Attempting to correct JSON using WatsonxLLM")

        # Prompt to correct the invalid JSON
        prompt = '''You are a JSON formatter. You will be given an invalid JSON string and the Python error encountered when trying to load it using json.loads(). Your job is to correct the invalid JSON string by considering the error message and return the correct JSON only as output, no additional text.

Invalid JSON String: """{json_text}"""

Python error message: """{error_msg}"""

Corrected JSON: '''
        corrected_json_response = watsonx_llm.generate_text(
            prompt.format(json_text=json_text, error_msg=str(e))
        )
        json_obj = json.loads(extract_json(corrected_json_response))

    return json_obj


class JsonPayload(BaseModel):
    json_text: str


@app.post("/parse_json/")
def parse_json(payload: JsonPayload):
    """
    Endpoint to parse JSON from the provided payload.

    Args:
    payload (JsonPayload): JSON payload containing the text to be parsed.

    Returns:
    dict: Parsed JSON object.
    """
    try:
        parsed_json = json_parser(payload.json_text)
        print(parsed_json)
        return parsed_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing JSON: {str(e)}")
