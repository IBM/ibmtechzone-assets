from dotenv import load_dotenv
import re
import json
import os
from genai import Client
from genai.credentials import Credentials
from genai.schema import TextGenerationParameters
import json
from transformers import AutoTokenizer
from prompts import META_PROMPT


class Backend:
    def __init__(self, model_id="google/flan-ul2", params=None):
    # Initialize the backend with credentials from environment variables
        load_dotenv()
        credentials = Credentials.from_env()
        self.client = Client(credentials=credentials)
        self.model_id = model_id
      
      # Define default parameters if none provided
        default_params = {
            "decoding_method": "greedy",
            "min_new_tokens": 1,
            "max_new_tokens": 2000,
            "stop_sequences":['\n\n\n']
        }
        
        self.params = default_params if params is None else {**default_params, **params}
        #self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_model_id)
      
    def send_to_genai(self, prompts):
      if not isinstance(prompts, list):
          prompts = [prompts]
      text_generation_params = TextGenerationParameters(**self.params)


      # Call the GenAI API, which returns a generator
      response_generator = self.client.text.generation.create(
          model_id=self.model_id,
          inputs=prompts,
          parameters=text_generation_params
      )

      # Iterate over the generator to get the results
      generated_texts = []
      for response in response_generator:
          for result in response.results:
              generated_texts.append(result.generated_text)

      return generated_texts[0]
    def build_prompt(self,task):
        prompt=META_PROMPT.format(task=task)
        return prompt
  
def main():
    model_id = "meta-llama/llama-3-70b-instruct"
    backend = Backend(model_id=model_id)
    task='write an email for resolving customer complaints about a product.'
    prompt=backend.build_prompt(task=task)
    print(prompt)
    response=backend.send_to_genai(prompt)
    print(response)
if __name__ == '__main__':
  main()