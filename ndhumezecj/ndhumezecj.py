import asyncio
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.foundation_models import Model

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

async def generate_response(model, prompt, gen_parms_override):
  
  def get_response():
      generated_response = model.generate(prompt, gen_parms_override)
      response = generated_response['results'][0]['generated_text']
      formatted_responss = '\n'.join([line.strip() for line in response.split('\n') if line.strip()])
      return formatted_responss

  return await asyncio.to_thread(get_response)

async def handle_prompts_async(model, prompts, gen_parms_override):
  tasks = []
  for prompt_key, prompt_template in prompts.items():
      prompt = prompt_template
      task = generate_response(model, prompt, gen_parms_override)
      tasks.append(task)

  responses = await asyncio.gather(*tasks)
  return {prompt_key: response for prompt_key, response in zip(prompts.keys(), responses)}
    
    
async def main():
  results = await handle_prompts_async(model, prompts, gen_parms_override)
  print(results)
  return results

asyncio.run(main())