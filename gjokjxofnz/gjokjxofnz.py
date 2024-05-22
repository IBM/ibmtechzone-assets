import os
import pandas as pd
from dotenv import load_dotenv
from prompt.prompt import *
from langchain.docstore.document import Document
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.auto import partition
from unstructured.staging.base import elements_to_json
from genai.schema import TextGenerationParameters, TextGenerationReturnOptions
from dotenv import load_dotenv
import re
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

TABLE_SUMMARIZATION_PROMPT = """
<Instructions>
Summarise the following HTML table in detail and specify all the points from table:
</Instructions>
<HTML table>
{html_table}
</HTML table>

Summary:

"""
GRANITE_RAG_CHAT_PROMPT ="""
<|system|>
You are Granite Chat, an AI language model developed by IBM. You are a cautious assistant. You carefully follow instructions. You are helpful and
harmless and you follow ethical guidelines and promote positive behavior.
<|user|>
You are a AI language model designed to function as a specialized Retrieval Augmented Generation (RAG) assistant. When generating responses,
prioritize correctness, i.e., ensure that your response is correct given the context and user query, and that it is grounded in the context.
Furthermore, make sure that the response is supported by the given document or context. Always make sure that your response is relevant to the question.Read through the information and do not mention "as shown in Figure" or "as shown in image" in the final answer.
Answer the question in 2 to 3 sentences. Do not  quote source of the document or share where it can be found.

[Document]
{context_document}
[End]
{query}
<|assistant|>
"""

############################## ############################## Watsonx Calling Function############################## ############################## 


user_bam = True

if user_bam:
    from genai import Credentials, Client
else:
    from ibm_watson_machine_learning.foundation_models import Model

load_dotenv()

if user_bam:
    # Configure workbench/bam

    creds = Credentials.from_env()
    client = Client(credentials=creds)
    
else:
    # Configure GA version
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

def send_to_watsonxai(prompts,
                    model_name="google/flan-ul2",
                    decoding_method="greedy",
                    max_new_tokens=100,
                    min_new_tokens=1,
                    temperature=1.0,
                    repetition_penalty=1.0, 
                    stop_sequences=None,
                    random_seed=42
                    ):
    '''
    helper function for sending prompts and params to Watsonx.ai
    
    Args:  
        prompts:list list of text prompts
        decoding:str Watsonx.ai parameter "sample" or "greedy"
        max_new_tok:int Watsonx.ai parameter for max new tokens/response returned
        temp:float Watsonx.ai parameter for temperature (range 0>2)

    Returns: None
        prints response
    '''

    global user_bam

    if user_bam: 
        # Workbench/BAM
        # Instantiate parameters for text generation
        
        responses = list(
            client.text.generation.create(
        model_id=model_name,
        inputs=prompts,
        
        parameters=TextGenerationParameters(
        max_new_tokens=200,
        min_new_tokens=20,
        random_seed =42,
        return_options=TextGenerationReturnOptions(
            input_text=True,
        )
        )
            )
    )
        return responses[0].results[0].generated_text
        
        
        
       
        
    
    else:
        # GA version
        model_params = {
            GenParams.DECODING_METHOD: decoding_method,
            GenParams.MIN_NEW_TOKENS: min_new_tokens,
            GenParams.MAX_NEW_TOKENS: max_new_tokens,
            GenParams.RANDOM_SEED: random_seed,
            GenParams.TEMPERATURE: temperature,
            GenParams.REPETITION_PENALTY: repetition_penalty,
            GenParams.STOP_SEQUENCES: stop_sequences
        }

        # GA
        model = Model(
                model_id=model_name,
                params=model_params,
                credentials=creds,
                project_id=project_id)
    
        # GA
        for prompt in prompts:
            return model.generate_text(prompt)
########################################################### ############################## ############################## ############################## ############################## 
############################################################ TABLE EXTRACTION AND SUMMARIZATION############################################################
documents = ['abc.pdf', '123.pdf', 'hello.pdf']
extracted_pdfs={}

import glob
files = glob.glob("/Users/docs/*.pdf")

# Extraction of tables
for i in files:
    filename = i.split('/')[-1]
    if filename in documents: # list of pdfs path
        elements = partition_pdf(filename=i, infer_table_structure=True, strategy='hi_res')
        extracted_pdfs[filename] = elements

#Creating chunks 
def create_chunks(dictionary):
    chunk_dictionary={}
    for filename,extracted_pdf_text in dictionary.items():
        text_chunks = []
        recent_title = "None"
        if filename not in chunk_dictionary.keys():
              
            for element in extracted_pdf_text:               
                if element.category == 'Title':
                    recent_title = element.text.strip()
                elif element.category == 'NarrativeText':
                    text = element.text.strip()
                    if recent_title is not None:
                        doc = Document(page_content=text, metadata={"filename": element.metadata.filename,"page_number": element.metadata.page_number,
                                                                     'Title':recent_title})
                    else:
                        doc = Document(page_content=text, metadata={"filename": element.metadata.filename,"page_number": element.metadata.page_number,
                                                                     'Title':"None"})
                    
                    text_chunks.append(doc)
                elif element.category == 'Table':
                    html_content = element.metadata.text_as_html
                    table_title = "None"
                    for prev_element in reversed(extracted_pdf_text[:extracted_pdf_text.index(element)]):
                        if prev_element.text.startswith('Table'):
                            table_title = prev_element.text.strip()
                            break
                    text = send_to_watsonxai(
                    prompts=[TABLE_SUMMARIZATION_PROMPT.format(html_table=html_content)],
                    model_name="ibm-mistralai/mixtral-8x7b-instruct-v01-q",
                    decoding_method='sample',
                    max_new_tokens=500,
                    min_new_tokens=10,
                    temperature=0.1,
                    repetition_penalty=1.1,
                    stop_sequences=[]
                )
                    doc = Document(page_content=text, metadata={"filename": element.metadata.filename,"page_number": element.metadata.page_number,
                                                                     'Title':table_title})
                    
                    text_chunks.append(doc)


            


            chunk_dictionary[filename] = text_chunks
    return chunk_dictionary

milvus_chunks = create_chunks(extracted_pdfs)

# Setting up Milvus DB
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)

connections.connect(host= '161.156.197.243', port="8080", secure=True, server_pem_path="cert.pem",server_name="localhost",user="root",password="4XYg2XK6sMU4UuBEjHq4EhYE8mSFO3Qq")

from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import Milvus
embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")

    

for filename,text_chunks in milvus_chunks.items():
    Milvus.from_documents(
        text_chunks,
        embeddings,
        connection_args={"host": "161.156.200.27", "port":"8080", "secure":True, "server_pem_path":"/Users/amithhooli/Projects/SEMI-STRUCT/notebooks/cert.pem",
                                            "server_name":"localhost","user":"root","password":"4XYg2XK6sMU4UuBEjHq4EhYE8mSFO3Qq"},
        collection_name=f'Milvus_all_docs_with_tables'
    )

MilvusDB_pdfall_tables =Milvus(embeddings,connection_args={
               "host": '161.161.161.161', "port":"8080", "secure":True, "server_pem_path":"cert.pem",
                                                "server_name":"localhost","user":"root","password":"4XYg2XK6sMU4UuBEjHq4EhYE8mSFO3Qq"},
                      collection_name='Milvus_all_docs_with_tables')




ret_docs = MilvusDB_pdfall_tables.max_marginal_relevance_search(query,k=10)

query = "What are the different life cycle stages"
_docs = pd.DataFrame([(query, doc.page_content) for doc in ret_docs], columns=['query', 'paragraph'])
response_1 = send_to_watsonxai(
                    prompts=[GRANITE_RAG_CHAT_PROMPT.format(context_document="\n\n".join(_docs['paragraph']), query=query)],
                    #model_name='meta-llama/llama-2-70b-chat',
                    model_name ="ibm/granite-13b-chat-v2",
                    decoding_method='sample',
                    max_new_tokens=200,
                    min_new_tokens=10,
                    temperature=0.1,
                    repetition_penalty=1.1,
                    stop_sequences=[]
                )
print(response_1)