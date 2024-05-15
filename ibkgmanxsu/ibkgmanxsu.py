
import ast
import re
from genai import Client
from genai.credentials import Credentials
from genai.schema import TextGenerationParameters
from dotenv import load_dotenv


class QueryModification:
    """ 
    Class for modifying queries and splitting complex queries into smaller, 
    separate queries for more effective retrieval from the database.
    """
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
       
        
    
    def query_modification_prompt(self, query):  
        """ Generate prompts for modifying the given query."""
        
        prompt = f"""[INST]
In your role as an intelligent assistant, your task is to process user queries by following these steps:
-You will be given a user query that might involve multiple elements or subjects.
-Your task is to process this user query to identify key elements and intents.
-Then, classify the query as either 'simple' or 'complex':
-A 'simple' query focuses on a specific element (intent) and pertains to a single subject.
-A 'complex' query involves multiple elements (intents) and/or multiple subjects.
-For complex queries, break them down into simpler components.
-If the query is simple, keep it as is.
-Return the new user queries as a Python list  like:
  Output:['new query 1', 'new query 2', ... ]
-Do not output anything other than the response. No explanations are needed.
User Query:{query}
Output:[/INST]
"""
        return prompt
       
   
    def generate_queries(self,org_query:str):  
        """Generate mutlpile queries from the original query """               
        
        prompt = self.query_modification_prompt(org_query) 
        response=self.send_to_genai(prompt)
        queries = response.replace("Output:","").strip()
        queries =list(eval(queries))        
        return queries
  
        
   # use the queries to retrieve relevant chunks from the vector database.
            
      


    

    
