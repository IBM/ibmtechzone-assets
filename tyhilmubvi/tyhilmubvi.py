from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.foundation_models import Model
import concurrent.futures
import os
PROMPT_1 = os.environ["prompt_1"]
PROMPT_2 = os.environ["prompt_2"]
PROMPT_3 = os.environ["prompt_3"]
PROMPT_4 = os.environ["prompt_4"]
API_KEY = os.environ["api_key"]
PROJECT_ID = os.environ["project_id"]

model = "meta-llama/llama-2-70b-chat"


my_credentials = { 
  "url"    : "https://us-south.ml.cloud.ibm.com",
  "apikey" : API_KEY
}
# params_response_generation = GenerateParams(decoding_method="greedy", min_new_tokens= min_new_tokens, max_new_tokens=max_new_tokens, random_seed=1024, repetition_penalty=1.2) 

model_id    = ModelTypes.LLAMA_2_70B_CHAT
gen_parms   = {"decoding_method" : "greedy", "min_new_tokens" : 10, "max_new_tokens" : 250, "random_seed" : 1024}
project_id  = PROJECT_ID
space_id    = None
verify      = False

model = Model( model_id, my_credentials, gen_parms, project_id, space_id, verify )   



prompt_1 = PROMPT_1
prompt_2 = PROMPT_2
prompt_3 = PROMPT_3
prompt_4 = PROMPT_4


prompts = {"Task1" : prompt_1,
  "Task2" : prompt_2,
  "Task3" : prompt_3,
  "Task4" : prompt_4
  }

gen_parms_override = None

results = {}

def multiple_api_calls(k):
    generated_response = model.generate( prompts[k], gen_parms_override )
    response = generated_response['results'][0]['generated_text']
    results[k] = '\n'.join([line.strip() for line in response.split('\n') if line.strip()])
    return results

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(multiple_api_calls, prompts.keys()))[0]
    ordered_results = {'Task1': results.get('Task1'), 'Task2': results.get('Task2'), 'Task3': results.get('Task3'), 'Task4': results.get('Task4') }
    print(ordered_results)