from dotenv import load_dotenv
import os
import re
import json
from transformers import AutoTokenizer
from genai import Client 
from genai.credentials import Credentials
from genai.schema import TextGenerationParameters
import ast



class Backend_triple:

    def __init__(self,tokenizer_model_id="mistralai/Mixtral-8x7B-Instruct-v0.1",model_id="google/flan-ul2", params=None):
    # Initialize the backend with credentials from environment variables
      api_key = os.environ["api_key"]
      self.credentials = Credentials(api_key)
      self.client = Client(credentials=self.credentials)
      self.model_id = model_id
      
      # Define default parameters if none provided
      default_params = {
          "decoding_method": "greedy",
          "min_new_tokens": 1,
          "max_new_tokens": 4000,
          "stop_sequences":['\n\n\n']
      }
      
      self.params = default_params if params is None else {**default_params, **params}
      self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_model_id)
      
    def send_to_genai(self, prompts):
        if not isinstance(prompts, list):
            prompts = [prompts]
        text_generation_params = TextGenerationParameters(**self.params)
        response_generator = self.client.text.generation.create(
            model_id=self.model_id,
            inputs=prompts,
            parameters=text_generation_params
        )

        #Iterate over the generator to get the results
        generated_texts = []
        for response in response_generator:
            for result in response.results:
                generated_texts.append(result.generated_text)

        return generated_texts
      
    def triple_for_single_chunk_prompt(self,ontology,text):
        prompt=f"""
        <<SYS>>
you are an expert in knowledge graph creation, your job is to help extract the triples from the given ontology for a knowledge graph from text provided by following the steps given below
<</SYS>>
[INST]
- first take a look at the text provided below within <text> </text> tags  about the given ontology {ontology} 
- you are given the combined ontology, the ontology that has been curated using different chunks of data
- you have to go through each of the given chunk using the combined ontology and then finally extract the knowledge triples for each of them while making sure the extracted knowledge triples are unique 
- now look at the given ontology and extract all the knowledge triples from it 
- show only the knowledge triples in the output and not the ontology schema 
- give me the output in a valid JSON format, while also making sure that all the attributes and relationships are being maintained from the given ontology
- for the final output show me the extracted knowledge triples
- a knowledge triple is a clause that contains a subject, a predicate, and an object
- the subject is the entity being described, the predicate is the property of the subject that is being described, and the object is the value of the property
- now while you are extracting the knowledge triple, I want you to check the relevant subject, predicate, and object from the given text and then give me the triple accordingly
- once you identify all the classes, define the attributes and properties for each of the classes.try to use the same words as mentioned in the text while defining the knowledge triple
- I want the output to be in a JSON format, which includes the class name or relationship name and its corresponding extracted value
- give the output of the knowledge triple in a JSON format , the key should be the ontology class name or relationship name and the value is the extracted value. Give it in legible manner. so that I can construct a proper knowledge graph with it.
- You don't have to show the ontology on the output, it is just for you to learn
- think step by step
- give the output as knowledge triple schema in JSON format within <JSON> </JSON> tags as shown in the examples below.
- learn from the examples given below:
<example>
text:
<text>
England is a country that is part of the United Kingdom.[6] The country is located on the island of eand borders with Scotland to the north and Wales to the west, and is otherwise surrounded by the North Sea to the east, the English Channel to the south, the Celtic Sea to the south-west, and the Irish sea to the west. Continental Europe lies to the south-east, and Ireland to the west. The population was 56,490,048 at the 2021 census. London is both the largest city and the capital.
The area now called England was first inhabited by modern humans during the Upper Paleolithic, but takes its name from the Angles, a Germanic tribe who settled during the 5th and 6th centuries. England became a unified state in the 10th century and has had a significant cultural and legal impact on the wider world since the Age of Discovery, which began during the 15th century.[7] The Kingdom of England, which included Wales after 1535, ceased being a separate sovereign state on 1 May 1707 when the Acts of Union put the terms agreed in the Treaty of Union the previous year into effect; this resulted in a political union with the Kingdom of Scotland that created the Kingdom of Great Britain.[8]
England is the origin of many well-known worldwide exports, including the English language, the English legal system (which served as the basis for the common law systems of many other countries), association football, and the Church of England; its parliamentary system of government has been widely adopted by other nations.[9] The Industrial Revolution began in 18th-century England, transforming its society into the world's first industrialised nation.[10] England is home to the two oldest universities in the English-speaking world: the University of Oxford, founded in 1096, and the University of Cambridge, founded in 1209. Both universities are ranked among the most prestigious in the world.[11][12]
England's terrain chiefly consists of low hills and plains, especially in the centre and south. Upland and mountainous terrain is mostly found in the north and west, including Dartmoor, the Lake District, the Pennines, and the Shropshire Hills. The country's capital is London, the greater metropolitan of which has a population of 14.2 million as of 2021, representing the United Kingdom's largest metropolitan area. England's population of 56.3 million comprises 84% of the population of the United Kingdom,[13] largely concentrated around London, the South East, and conurbations in the Midlands, the North West, the North East, and Yorkshire, which each developed as major industrial regions during the 19th century.[14]
</text>
Now based on the provided text about England, the following is the ontology for the a knowledge graph:
ontology:
{{
  "classes": {{
    "Country": {{
      "attributes": ["Name", "Part of", "Land Borders", "Surrounded by", "Population", "Capital"]
    }},
    "Geographical Feature": {{
      "attributes": ["Name", "Type", "Location"]
    }},
    "Population Census": {{
      "attributes": ["Year", "Population"]
    }},
    "City": {{
      "attributes": ["Name", "Status", "Population"]
    }},
    "Historical Event": {{
      "attributes": ["Name", "Description", "Date"]
    }},
    "Legal System": {{
      "attributes": ["Name", "Influence"]
    }},
    "Sport": {{
      "attributes": ["Name", "Origin"]
    }},
    "Religious Institution": {{
      "attributes": ["Name", "Established Religion"]
    }},
    "Government System": {{
      "attributes": ["Name", "Influence"]
    }},
    "Industrial Revolution": {{
      "attributes": ["Start Date", "Description", "Impact"]
    }},
    "University": {{
      "attributes": ["Name", "Founded Year", "Ranking"]
    }},
    "Terrain Type": {{
      "attributes": ["Name", "Description", "Location"]
    }}
  }},
  "relationships": {{
    "Country": {{
      "contains": ["City", "Geographical Feature", "University"],
      "originates": ["Legal System", "Sport", "Religious Institution", "Government System"],
      "settingFor": "Historical Event",
      "began": "Industrial Revolution"
    }},
    "City": {{
      "containedBy": "Country"
    }}
  }}
}}
Now take a look at the above ontology and based on it, this is how the extracted knowledge triple should look like. You have to extract the knowledge triples accordingly. 
The following is the resultant knowledge triple for the above ontology
Knowledge Triple:
<JSON>
{{
  "knowledgeTriples": [
    {{
      "Country": "England",
      "predicate": "hasPartOf",
      "Country": "United Kingdom" 
    }},
    {{
      "Country": "England",
      "predicate": "hasLandBorder",
      "Country": "Scotland"
    }},
    {{
      "Country": "England",
      "predicate": "hasLandBorder",
      "Country": "Wales"
    }},
    {{
      "Country": "England",
      "predicate": "surroundedBy",
      "Geographical Feature": "North Sea" 
    }},
    {{
      "Country": "England",
      "predicate": "surroundedBy",
      "Geographical Feature": "English Channel"
    }},
    {{
      "Country": "England",
      "predicate": "surroundedBy",
      "Geographical Feature": "Celtic Sea"
    }},
    {{
      "Country": "England",
      "predicate": "surroundedBy",
      "Geographical Feature": "Irish Sea"
    }},
    {{
      "Country": "England", 
      "predicate": "adjacentTo", 
      "Geographical Feature": "Continental Europe" 
    }}, 
    {{
      "Country": "England",
      "predicate": "adjacentTo",
      "Country": "Ireland"  
    }},
    {{
      "Country": "England",
      "predicate": "hasPopulation",
      "Population Census": {{
        "value": "56490048",
        "censusYear": "2021"
      }}
    }},
    {{
      "Country": "England",
      "predicate": "hasCapital",
      "City": "London"
    }},
    {{
      "City": "London",
      "predicate": "locatedIn",
      "Country": "England"
    }},
    {{
      "City": "London",
      "predicate": "hasStatus",
      "object": "Capital and Largest City" 
    }},
    {{
      "City": "London",
      "predicate": "hasPopulation",
      "Population Census": {{ 
        "value": "14200000",
        "type": "metropolitan area" 
      }} 
    }},
    {{
      "Country": "England",
      "predicate": "originOf",
      "Language": "English" 
    }}, 
    {{
      "Country": "England",
      "predicate": "originOf",
      "Legal System": "English legal system" 
    }},
    {{
      "Country": "England",
      "predicate": "originOf",
      "Sport": "association football"
    }},
    {{
      "Country": "England",
      "predicate": "hasOfficialReligion",
      "Religious Institution": "Church of England"
    }},
    {{
      "Country": "England",
      "predicate": "originOf",
      "Government System": "parliamentary system" 
    }},
    {{
      "Country": "England",
      "predicate": "experienced",
      "Historical Event": {{ 
        "name": "Industrial Revolution",
        "startDate": "18th-century",
        "description": "transforming its society into the world's first industrialised nation",
        "impact": "Significant"
      }}
    }}
  ] 
}} 
</JSON>
</example>
[/INST]
text:
<text>
{text}
</text>
ontology:
<ontology>
{ontology}
</ontology>
Output:"""
        
        return prompt
    #function to build prompt which takes the individual triples and merges them into one knowledge triple
    def triple_consolidation_prompt(self, triples):

        prompt = f"""<<SYS>>
you are an expert in knowledge graph creation, your job is to take a look at a number of knowledge triples provided to you in JSON format and consolidate all of them into a single meaningful set of knowledge triples by following the instructions given below:
<</SYS>>
[INST]
Step 1: Merge all the knowledge triples:
- Merge all the knowledge triples {triples} that are being extracted 
- The corresponding knowledge triples are given to you in a JSON format
- You are given knowledge triples from many chunks of data
- Create a new knowledge triple schema that includes all the knowledge triples extracted
- Ensure that the final knowledge triple maintains logical consistency and integrity
- The merged knowledge triple should be in a valid JSON format within the tags <JSON> </JSON>

Learn from the following example 

<example>
kt1:
<JSON>
{{
  "knowledgeTriples": [
    {{
      "Country": "England",
      "predicate": "hasPartOf",
      "Country": "United Kingdom" 
    }},
    {{
      "Country": "England",
      "predicate": "hasLandBorder",
      "Country": "Scotland"
    }},
    {{
      "Country": "England",
      "predicate": "hasLandBorder",
      "Country": "Wales"
    }},
    {{
      "Country": "England",
      "predicate": "surroundedBy",
      "Geographical Feature": "North Sea" 
    }},
    {{
      "Country": "England",
      "predicate": "surroundedBy",
      "Geographical Feature": "English Channel"
    }},
    {{
      "Country": "England",
      "predicate": "surroundedBy",
      "Geographical Feature": "Celtic Sea"
    }},
    {{
      "Country": "England",
      "predicate": "surroundedBy",
      "Geographical Feature": "Irish Sea"
    }},
    {{
      "Country": "England", 
      "predicate": "adjacentTo", 
      "Geographical Feature": "Continental Europe" 
    }}, 
    {{
      "Country": "England",
      "predicate": "adjacentTo",
      "Country": "Ireland"  
    }},
    {{
      "Country": "England",
      "predicate": "hasPopulation",
      "Population Census": {{
        "value": "56490048",
        "censusYear": "2021"
      }}
    }},
    {{
      "Country": "England",
      "predicate": "hasCapital",
      "City": "London"
    }},
    {{
      "City": "London",
      "predicate": "locatedIn",
      "Country": "England"
    }},
    {{
      "City": "London",
      "predicate": "hasStatus",
      "object": "Capital and Largest City" 
    }},
    {{
      "City": "London",
      "predicate": "hasPopulation",
      "Population Census": {{ 
        "value": "14200000",
        "type": "metropolitan area" 
      }} 
    }},
    {{
      "Country": "England",
      "predicate": "originOf",
      "Language": "English" 
    }}, 
    {{
      "Country": "England",
      "predicate": "originOf",
      "Legal System": "English legal system" 
    }},
    {{
      "Country": "England",
      "predicate": "originOf",
      "Sport": "association football"
    }},
    {{
      "Country": "England",
      "predicate": "hasOfficialReligion",
      "Religious Institution": "Church of England"
    }},
    {{
      "Country": "England",
      "predicate": "originOf",
      "Government System": "parliamentary system" 
    }},
    {{
      "Country": "England",
      "predicate": "experienced",
      "Historical Event": {{ 
        "name": "Industrial Revolution",
        "startDate": "18th-century",
        "description": "transforming its society into the world's first industrialised nation",
        "impact": "Significant"
      }}
    }}
  ] 
}} 
</JSON>
</example>
[/INST]
text:
<text>
{text}
</text>
ontology:
<ontology>
{ontology}
</ontology>
Output:"""
        
        return prompt
    #function to build prompt which takes the individual triples and merges them into one knowledge triple
    def triple_consolidation_prompt(self, triples, ontology):

        prompt = f"""<<SYS>>
    you are an expert in knowledge graph creation, your job is to take a look at a number of knowledge triples provided to you in JSON format and consolidate all of them into a single meaningful set of knowledge triples by following the instructions given below:
    <</SYS>>
    [INST]
    Step 1: Merge the knowledge triples:
    - Merge all the knowledge triples {triples} extracted for each chunk, while using the given {ontology}
    - Create a new knowledge triple schema that includes all unique knowledge triples extracted from the input ontology.
    - Ensure that the final knowledge triple maintains logical consistency and integrity
    - the merged knowledge triple should be within <JSON> </JSON> tags.

    Output:
            """
        return prompt
    
    def read_json_file(self,file_path):
        with open(file_path,'r') as file:
            return json.load(file)
            
    #function to chunk the data
    def chunk_texts(self,data, max_tokens=10000, overlap_words=100):
        chunks = []
        current_chunk_tokens = []
        current_tokens_count = 0
        overlap_tokens = []

        for item in data:
            text = item['page_text']
            text_tokens = self.tokenizer.tokenize(text)

            for token in text_tokens:
                current_chunk_tokens.append(token)
                current_tokens_count += 1

                    # Add tokens to the overlap buffer
                if len(overlap_tokens) < overlap_words:
                    overlap_tokens.append(token)
                else:
                    overlap_tokens.pop(0)
                    overlap_tokens.append(token)

                if current_tokens_count >= max_tokens:
                        # Convert current chunk tokens to string and add to chunks
                    chunk_text = self.tokenizer.convert_tokens_to_string(current_chunk_tokens)
                    chunks.append(chunk_text)

                        # Start new chunk with overlap if there are enough tokens
                    if len(overlap_tokens) == overlap_words:
                        overlap_text = self.tokenizer.convert_tokens_to_string(overlap_tokens)
                        current_chunk_tokens = self.tokenizer.tokenize(overlap_text)
                        current_tokens_count = len(current_chunk_tokens)
                    else:
                        current_chunk_tokens = []
                        current_tokens_count = 0

            # Add the last chunk if it has content
        if current_chunk_tokens:
            chunk_text = self.tokenizer.convert_tokens_to_string(current_chunk_tokens)
            chunks.append(chunk_text)

        return chunks
        
    def extract_and_convert_json(self,input_strings):
                  # Regular expression to extract text between <JSON> and </JSON>
        pattern = r'<JSON>(.*?)</JSON>'
            

            # Process each string in the input list
        for input_string in input_strings:
                # Find all occurrences of the pattern
            matches = re.findall(pattern, input_string, re.DOTALL)

                # Process each match
            for match in matches:
                try:
                    json_object = ast.literal_eval(match)
                    return json_object
                except json.JSONDecodeError:
                    print(f"Warning: A match was found but it's not valid JSON: {match}")
                    continue
                except Exception as e:
                    print("Error",e)
                    continue

        return []
        
        #building prompts for each chunk
    
    def build_prompts_for_individual_triple(self, chunks, ontology):
        prompts = []
        for chunk in chunks:
          if len(chunk) < 50:
            continue
          prompts.append(self.triple_for_single_chunk_prompt(text=chunk, ontology=ontology))
        return prompts
        
        #generating triples for each chunk
    
    def generate_triples(self, prompts):
        responses = self.send_to_genai(prompts=prompts)
        print("responses: ",responses)
        triples = self.extract_and_convert_json(responses)
        return triples
        
    #merging all the triples
    def merge_triples(self, triples):
        merged_triple_prompt = self.triple_consolidation_prompt(triples=json.dumps(triples))
        #print("prompt",merged_triple_prompt)
        final_response = self.send_to_genai(prompts=[merged_triple_prompt])
        #print("FINAL",final_response)
        merged_triple = self.extract_and_convert_json(final_response)
        print("merged",merged_triple)

            #Write merged triple to a json file
        with open('merged_triple.json','w') as file:
            json.dump(merged_triple, file)

        return merged_triple
        
    def read_and_chunk_data(self, file_path):
        data = self.read_json_file(file_path=file_path)
        chunks = self.chunk_texts(data)
        return chunks
    
    def split_page_into_chunks(self,page_text, max_tokens=10000, overlap_words=100):
        chunks = []
        tokens = self.tokenizer.tokenize(page_text)
        text_length = len(tokens)
        if text_length <= max_tokens:
            chunks.append(page_text)
        else:
            
            start = 0
            while start < text_length:
                chunk_tokens = tokens[start:start + max_tokens]
                chunk_text = self.tokenizer.convert_tokens_to_string(chunk_tokens)
                chunks.append(chunk_text.strip())
                start += max_tokens - overlap_words
             
        return chunks

#mistral tokenizer for chunking    
def main():
    #tokenizer_model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    model_id = "mistralai/mixtral-8x7b-instruct-v0-1"
    backend = Backend_triple(model_id=model_id)
    file_path = os.environ["json_file_path"]    #Upload the unstructed data 
    #domain = "IBM technical documentation"
    ontology = os.environ["ontology_json"]  #Upload the ontology file 
    data = None 
    
    # Open the JSON file for reading
    with open(file_path, "r") as file:
        # Load the JSON data from the file
        data = json.load(file)
    # Now ‘data’ contains the JSON data as a Python dictionary or list
    output = {}
    for item in data:
        link = item["link"]
        page_text = item["page_text"]
        chunks = backend.split_page_into_chunks(page_text=page_text)
        print(chunks)
        print(len(chunks))
        prompts = backend.build_prompts_for_individual_triple(chunks, ontology) 
        #print(prompts)
        triples = backend.generate_triples(prompts) 
        print(triples)
        # merged_triple = backend.merge_triples(ontology, triples) 
        output[link] = {
            "triplets":triples
        }
    with open("output.json","w") as file:
        file.read(json.dumps(output,indent = 4))


if __name__ == "__main__":
    main()
  
        

    
    