from dotenv import load_dotenv 
import os
import re
from genai import Client
from genai.credentials import Credentials
from genai.schema import TextGenerationParameters
import json
load_dotenv()



class Backend:  
    def __init__(self, model_id="google/flan-ul2", params=None):
    # Initialize the backend with credentials from environment variables
      self.credentials = Credentials(api_key="")
      self.client = Client(credentials=self.credentials)
      self.model_id = model_id
      
      # Define default parameters if none provided
      default_params = {
          "decoding_method": "greedy",
          "min_new_tokens": 1,
          "max_new_tokens": 2000,
          "stop_sequences":['\n\n\n']
      }
      
      self.params = default_params if params is None else {**default_params, **params}

      
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

      return generated_texts

    def build_prompt(self,input: str):
        prompt= f"""<|begin_of_text|><|start_header_id|>You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:
        multiply: multiply(first_int: int, second_int: int) -> int - Multiply two integers together.
        add: add(first_int: int, second_int: int) -> int - Add two integers.
        exponentiate: exponentiate(base: int, exponent: int) -> int - Exponentiate the base to the exponent power.<|end_header_id|>
        
        - Given the user input, return the name and input of the tool to use. Return your response as a JSON FORMATTED with 'name' and 'arguments' keys.
        - think step by step
        - make sure the function arguments are integers of decimal numbers only, i dont want fractions
        - i dont want any code. i want only the function name and the right arguments
        - I  want the JSON output within <JSON> tags
        Example output:
        <JSON>
        {{
            "name": "add",
            "arguments": [16,15]
        }}    
        <JSON>
        <|eot_id|>
        <|start_header_id|>user<|end_header_id|> user input: {input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
        """
        return prompt
    
   

    def extract_json(self,text):
         # Debugging print
        print(text)  # Show the actual input
        pattern = r'<JSON>\s*(.*?)\s*<JSON>'
        match = re.search(pattern, text, re.DOTALL)
        if match:
              # Debugging print
            return match.group(1).strip()
         # Debugging print
        return None

    
    
    def call_tool(self,json_input):
        # Parse the JSON input
        data = json.loads(json_input)
        tool_name = data["name"]
        arguments = data["arguments"]

        # Retrieve the function based on tool_name and call it with the arguments
        if tool_name in tools:
            return tools[tool_name](*arguments)
        else:
            return "No such tool found"









if __name__ == "__main__":
    Backend = Backend("meta-llama/llama-3-70b-instruct")

    def multiply(first_int: int, second_int: int) -> int:
        """Multiply two integers together."""
        return first_int * second_int

    
    def add(first_int: int, second_int: int) -> int:
        "Add two integers."
        return first_int + second_int


    
    def exponentiate(base: int, exponent: int) -> int:
        "Exponentiate the base to the exponent power."
        return base**exponent
    
    tools = {
    "multiply": multiply,
    "add": add,
    "exponentiate": exponentiate
}

    prompt=Backend.build_prompt(input="")
    print(prompt)
    response=Backend.send_to_genai(prompts=prompt)
    print("response",response)
    function_json=Backend.extract_json(text=response[0])
    print("json",function_json)
    output = Backend.call_tool(function_json)
    print(output)


