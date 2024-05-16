import os
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from dotenv import load_dotenv

def get_wml_creds():
    load_dotenv()
    api_key = os.getenv("API_KEY", None)
    ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
    project_id = os.getenv("PROJECT_ID", None)
    if api_key is None or ibm_cloud_url is None or project_id is None:
        print("Ensure you copied the .env file that you created earlier into the same directory as this notebook")
    else:
        creds = {
            "url": ibm_cloud_url,
            "apikey": api_key 
        }
    return project_id, creds


project_id, creds = get_wml_creds()

greedy_params={
    "decoding_method": "greedy",
    # "stop_sequences": [
    #   "\n\n"
    # ],
    "min_new_tokens": 1,
    "max_new_tokens": 800,
    # "repetition_penalty": 1.25,
    "moderations": {
      "hap": {
        "input": "false",
        "threshold": 0.75,
        "output": "false"
      }
    }
  }

def send_to_watsonxai(prompts,
                    model_name='meta-llama/llama-2-70b-chat',
                    decoding_method='sample',
                    max_new_tokens=400,
                    min_new_tokens=10,
                    temperature=0.1,
                    repetition_penalty=1.1,
                    stop_sequences=["Input:","Question:"]
                    ):
    '''
    Author: Pinkal Patel
    helper function for sending prompts and params to Watsonx.ai
    
    Args:  
        prompts:list list of text prompts
        decoding:str Watsonx.ai parameter "sample" or "greedy"
        max_new_tok:int Watsonx.ai parameter for max new tokens/response returned
        temp:float Watsonx.ai parameter for temperature (range 0>2)

    Returns: None
        prints response
    '''
    #print("========== My Model =========")
    # GA version
    model_params = {
        GenParams.DECODING_METHOD: decoding_method,
        GenParams.MIN_NEW_TOKENS: min_new_tokens,
        GenParams.MAX_NEW_TOKENS: max_new_tokens,
        GenParams.RANDOM_SEED: 42,
        GenParams.TEMPERATURE: temperature,
        GenParams.REPETITION_PENALTY: repetition_penalty,
        GenParams.STOP_SEQUENCES: stop_sequences
    }

    # GA
    model = Model(
            model_id=model_name,
            params=greedy_params,
            credentials=creds,
            project_id=project_id)

    # GA
    for prompt in prompts:
        return model.generate_text(prompt)

prompt_input = """You will be provided with transcript. Your task is to first read transcript, correct the spelling of the words which are misspelled, masked the sensitive information.
Input: {transcript}

Output:"""

def get_watson_ai_output(transcript):
    try:
        response_1 = send_to_watsonxai(
                            prompts=[prompt_input.format(transcript=transcript)],
                            #model_name='google/flan-t5-xxl',
                            model_name='meta-llama/llama-3-70b-instruct',
                            decoding_method='greedy',
                            max_new_tokens=4096,
                            min_new_tokens=10,
                            temperature=0.1,
                            repetition_penalty=1,
                            stop_sequences=["Note:"]
                        )
    except:
        print("Error while calling watson ai")
    return response_1
