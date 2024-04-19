from dotenv import load_dotenv
from genai import Client
from genai.credentials import Credentials
from weaviate_wrapper import WeaviateWrapper
import os
import json


class GenerateLLMResponse:
    def __init__(self,model_id = "meta-llama/llama-2-70b-chat",generation_params = {
                "decoding_method": "sample",
                "max_new_tokens": 512,
                "stop_sequences": ["\n\n\n"],
                "temperature": 0.1,
                "top_k": 50,
                "top_p": 1,
                "repetition_penalty": 1
                },weaviate_host_url = "http://localhost:8080",
    embedding_model_name = "intfloat/e5-large-v2",):
        # Load credentials
        load_dotenv()
        self.client = Client(credentials=Credentials.from_env())
        self.model_id = model_id
        self.parameters = generation_params
        self.ww = WeaviateWrapper(host = weaviate_host_url,embedding_model_name = embedding_model_name)

    # Create the Prompt
    def build_prompt(self,question,context):
        prompt = f'''<|system|>
'You are Granite Chat, an AI language model developed by IBM. You are a cautious assistant. You carefully follow instructions. You are helpful and harmless and you follow ethical guidelines and promote positive behavior.
<|user|>
You are a AI language model designed to function as a specialized Retrieval Augmented Generation (RAG) assistant.
When generating responses, prioritize correctness, i.e., ensure that your response is correct given the context and user query, and that it is grounded in the context.
Furthermore, make sure that the response is supported by the given document or context.
Always make sure that your response is relevant to the question and then give the final answer.
[Document]
{context}
[End]
Query: {question}
<|assistant|>\n
'''
        # Use the below prompt template for Granite model.
#         prompt=f'''Given the document and the current conversation between a user and an agent, your task is as follows: Answer any user query by using information from the document. The response should be detailed and should be written only in English.

# DOCUMENT: {context}
# DIALOG: USER: {question}
        return prompt
    
    def hypothetical_prompt(self, query, tokens=100):
        prompt = f'''<|system|>
You are Granite Chat, an AI language model developed by IBM.
You are a cautious assistant.
You carefully follow instructions.
You are helpful and harmless and you follow ethical guidelines and promote positive behavior.
Please do not say anything else apart from the answer and do not start a conversation.
<|user|>
You have to answer a given query. Please generate an answer under {tokens} tokens.
Query: {query}
<|assistant|>\n
'''
        return prompt
    def generate_hypothetical_answer(self, query, tokens =100):
        prompt = self.hypothetical_prompt(query)
        response = self.send_to_watsonxai(prompt)
        return response
    
    def perform_hyde(self, query, hypothetical_answer,ww_classname):
        query_to_search = query+'\n'+hypothetical_answer
        if 'Parent_child' in ww_classname:
            context = self.return_context(query,ww_classname,top_k=10,autocut=5)
            context = self.get_unique_strings_ordered(context)
        else:
            context = self.return_context_for_query(query = query_to_search, classname=ww_classname, top_k=10, autocut=5)
        return context
    
    
    def return_context_for_query(self,query,pdf="",classname="Rag",top_k=5,autocut=2):
        if pdf =="":
            data= self.ww.search_relevant_objects(user_query = query,classname=classname,parameters=["pdf","text","chunk_number"],top_k=top_k,autocut=autocut)
            #new_data = self.ww.get_unique_data(json.loads(data),"Rag")
            print(data)
            return self.parse_json_response_for_LLM(json.loads(data),classname)
        else:
            data= self.ww.hybrid_search_relevant_objects_where(user_query = query,classname=classname,parameters=["pdf","text","chunk_number"],pdf=pdf,top_k=top_k,autocut=autocut)
            #new_data = self.ww.get_unique_data(json.loads(data),"Rag")
            return self.ww.parse_json_response_for_LLM(json.loads(data),classname)
    
    def send_to_watsonxai(self,prompt):
        if isinstance(prompt, str):      
            for _, response in enumerate(self.client.text.generation.create(model_id=self.model_id, inputs = prompt, parameters=self.parameters)):
                return response.results[0].generated_text
        if isinstance (prompt,list):
            outputs = []
            for _, response in enumerate(self.client.text.generation.create(model_id=self.model_id, inputs = prompt, parameters=self.parameters)):
                outputs.append(response.results[0].generated_text)
            return outputs
        
    def generate_hyde_response(self, query, context):
        if isinstance(context, list):
            context = '\n'.join(context)
        elif isinstance(context, dict):
            context = '\n'.join([item['text'] for item in context])
        
        answer = self.answer_based_on_context_hyde(query, context)
        return answer
    
    def answer_based_on_context_hyde(self,query:str,context:str):
        '''
        Generates LLM response for a query based upon a context.
        Parameters:
        query: str
        context: str
        '''
        prompt = self.build_prompt(query,context)
        # print(prompt)
        result = self.send_to_watsonxai(prompt = prompt)
        return result
    