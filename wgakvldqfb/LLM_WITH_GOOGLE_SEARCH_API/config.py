# config.py

WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
WATSONX_API_KEY = "<API_KEY>"
WATSONX_MODEL_ID = "meta-llama/llama-2-70b-chat"
WATSONX_PARAMETERS = {
    "decoding_method": "greedy",
    "max_new_tokens": 200,
    "repetition_penalty": 1
}
WATSONX_PROJECT_ID = "<YOUR_WATSONX_PROJECT_ID>"
WATSONX_SPACE_ID = None  # Replace with actual space ID if needed

GOOGLE_API_KEY = "<YOUR_GOOGLE_API_KEY>"
GOOGLE_ENGINE_ID = "<YOUR_GOOGLE_ENGINE_ID>"
