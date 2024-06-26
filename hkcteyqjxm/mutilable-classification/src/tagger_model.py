import os
import getpass
from ibm_watsonx_ai.foundation_models import Model
from tagger import get_prompt_text, get_prompt_text_based_topic, get_prompt_test_cases, get_prompt_segregate
from langchain_ibm import WatsonxLLM
from langchain_experimental.llms import JsonFormer

def get_credentials():
    return {"url": os.getenv("GA_URL"), "apikey": os.getenv("GA_API_KEY")}

#model_id = "mistralai/mixtral-8x7b-instruct-v01"
#model_id = "meta-llama/llama-3-70b-instruct"
model_id = "ibm/granite-13b-chat-v2"

parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 200,
    "repetition_penalty": 1
}

decoder_schema = {
  "text": {"type": "string"},
  "description": {"type": "string"},
  "expectations": {"type": "string"}
}

project_id = os.getenv("GA_PROJECT_ID")

def str_array_to_array(arr_str):
    print(arr_str)
    start_index = arr_str.index('[')
    end_index = arr_str.index(']')
    actual_list = arr_str[start_index+1:end_index]
    print(actual_list)
    arr = []
    for item in actual_list.split(","):
        if item:
            arr.append(eval(item))
    return arr

def get_model_inference(input, model_option):
    model_id = "ibm/granite-13b-chat-v2"
    if model_option == "Mixtral":
        model_id = "mistralai/mixtral-8x7b-instruct-v01"
    elif model_option == "llama":
        model_id = "meta-llama/llama-3-70b-instruct"
    model = Model(
        model_id = model_id,
        params = parameters,
        credentials = get_credentials(),
        project_id = project_id,
        space_id = ""
        )
    prompt_input = get_prompt_text(input)
    generated_response = model.generate_text(prompt=prompt_input, guardrails=True)
    generated_response = str_array_to_array(generated_response)
    return generated_response

def get_model_inference_topic(input,topic, model_option):
    model_id = "ibm/granite-13b-chat-v2"
    if model_option == "Mixtral":
        model_id = "mistralai/mixtral-8x7b-instruct-v01"
    elif model_option == "llama":
        model_id = "meta-llama/llama-3-70b-instruct"
    model = Model(
        model_id = model_id,
        params = parameters,
        credentials = get_credentials(),
        project_id = project_id,
        space_id = ""
        )
    prompt_input = get_prompt_text_based_topic(input, topic)
    generated_response = model.generate_text(prompt=prompt_input, guardrails=True)
    return generated_response

def get_model_inference_test_case(requirement,support_text, topic):
    model_id = "meta-llama/llama-3-70b-instruct"
    parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 200,
    "repetition_penalty": 1
    }
    model = Model(
        model_id = model_id,
        params = parameters,
        credentials = get_credentials(),
        project_id = project_id,
        space_id = ""
        )
    prompt_input = get_prompt_test_cases(requirement,support_text, topic)
    #print(prompt_input)
    generated_response = model.generate_text(prompt=prompt_input, guardrails=True)
    #print(generated_response)
    model_id = "meta-llama/llama-3-70b-instruct"
    segregated_prompt = get_prompt_segregate(generated_response)
    model = Model(
        model_id = model_id,
        params = parameters,
        credentials = get_credentials(),
        project_id = project_id,
        space_id = ""
        )

    segregate_response = model.generate_text(prompt=segregated_prompt, guardrails=True)
    print("SEGREGATE")
    print(segregate_response[segregate_response.find('{'):segregate_response.find('}')+1])
    return prompt_input, segregate_response[segregate_response.find('{'):segregate_response.find('}')+1]