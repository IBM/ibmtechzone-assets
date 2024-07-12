# 1. Get Policy [Obligations, XX, YY] list from WD 
# 2. Chunck Contract and load to WxD
# 3. Compare Each obligation with contract
# 4. Show result

import pandas as pd
import copy
import os
import re
# from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from langchain.text_splitter import RecursiveCharacterTextSplitter,CharacterTextSplitter
from langchain.vectorstores.elasticsearch import ElasticsearchStore
# from langchain_elasticsearch import ElasticsearchStore
# from langchain.chains import RetrievalQA
from dotenv import load_dotenv
# from elasticsearch.helpers import scan, bulk
from tqdm import tqdm
from getpass import getpass
import time
import pandas as pd
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer
import json
from docx import Document
from ibm_watson_machine_learning.foundation_models import Model


def connection_toESDB():
    elasticsearch_url = ""
    username = ''
    password = ''

    cert_path = ''
    es_connection = Elasticsearch(
        elasticsearch_url,
        ca_certs=cert_path,
        basic_auth=(username, password))
    return es_connection



'''Currenlty this method loads the policy from a .txt file. 
TODO: 
1. Get the relevant policy (Obligation, Right, Exclusions) from Watson Discovery
2. Obligations are not grouped properly. TBC how to combine obligations. 
Return: List of Obligations'''
def get_policy_list(wd_configs=None, policy_name=None):
    with open('data/Policies/processed_nda_policy.txt', 'r') as file:
        # Read the text data from the file
        text_data = file.read()

    # Convert the text data to a list of dictionaries using eval()
    obligations_json = eval(text_data)

    obligations_queries=[] #TODO: Obligations are not grouped properly. TBC how to combine obligations. 
    # Loop through each obligation and perform tasks
    for obligation in obligations_json:
        for key, value in obligation.items():
            clean_value = '\n'.join([''.join(sublist) for sublist in value])
            obligations_queries.append(clean_value)
    
    return obligations_queries


'''TODO Contracts need to be fetched from Openpages and processed accordinly. '''
def read_contract_documents(doc_paths=["data/Contracts/NDA template from IP Australia.docx"]):
    data = []
    for idx, doc_path in enumerate(doc_paths):
        doc_id = f"doc_{idx + 1}"  # Generate a document ID
        doc = Document(doc_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        data.append({"id": doc_id, "text": text})  # Include document ID in the data
    return data


def create_index_and_embedings_contract_wxd(contract_data, es_connection,documents, index_name_write):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(contract_data)

    
    if es_connection.indices.exists(index=index_name_write):
        # es_connection.indices.delete(index=index_name_write)
        print(" Index Already exist") #TODO: Check how to update if there are any changes
    else:
        es_connection.indices.create(index=index_name_write, body={
            "mappings": {
                "properties": {
                    "contract_doc": {"type": "text"},
                    "embedding": {"type": "dense_vector", "dims": len(embeddings[0])}
                }
            }
        })

        # Index documents with embeddings into Elasticsearch
        for i, doc in enumerate(documents):
            doc["embedding"] = embeddings[i].tolist()
            es_connection.index(index=index_name_write, body=doc)

    doc_count = es_connection.count(index=index_name_write)["count"]
    print("Document count: ", doc_count)
    
    
def model_exists(es_connection, model_ID):
    try:
        es_connection.ml.get_trained_models(model_id=model_ID)
        return True
    except exceptions.NotFoundError:
        return False

def is_model_deployed(es_connection, model_ID):
    model_info = es_connection.ml.get_trained_models_stats(model_id=model_ID)
    return model_info["trained_model_stats"][0]["deployment_stats"]["state"] == "started"

def create_and_deploy_model(es_connection, model_ID=".elser_model_1"):
    if model_exists(es_connection, model_ID):
        if is_model_deployed(es_connection, model_ID):
            print("ELSER Model is already deployed.")
            return
    else:
        print("Model doesn't exist, creating one...")

    # Create or update the model configuration
    es_connection.ml.put_trained_model(
        model_id=model_ID, input={"field_names": ["text_field"]}
    )

    print("Model configuration created or updated.")

    if not model_exists(es_connection, model_ID):
        print("Starting model deployment...")
        # Start trained model deployment
        es_connection.ml.start_trained_model_deployment(
            model_id=model_ID, number_of_allocations=1, wait_for="starting"
        )

        # Wait for deployment to finish
        while True:
            if is_model_deployed(es_connection, model_ID):
                print("ELSER Model has been successfully deployed.")
                break
            else:
                print("ELSER Model is currently being deployed.")
            time.sleep(2)
    else:
        print("Model already exists and is not deployed. Skipping deployment.")


def batch_load_contract_data(documents, index_name_write,es_connection):
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, 
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
    )
    
    actions = []
    idx = 0
 
    text_chunks = text_splitter.split_text(documents)
    print(text_chunks)
    for chunk in text_chunks:
        action = {
                "index": index_name_write,
                "id": idx,
                "text": chunk
            }
        actions.append(action)
                #print(actions)
    
        
    New_dataFrame=pd.DataFrame(actions)
    docs_final = New_dataFrame.copy(deep=True)
    docs_final['id'] = docs_final.index.values
    if es_connection.indices.exists(index=index_name_write):
            es_connection.indices.delete(index=index_name_write)
            
    ELastic_upload(docs_final, index_name_write,es_connection, batch_size=100)  # Adjust batch_size as needed

def upload_batch(docs_batch, index_name_write,es_connection ):
    
    vector_store = ElasticsearchStore(es_connection=es_connection,
                                      index_name=index_name_write,
                                      strategy=ElasticsearchStore.SparseVectorRetrievalStrategy(model_id=".elser_model_1"))
    _ = vector_store.add_texts(texts=docs_batch.text.tolist(),
                               index_name=index_name_write,
                               ids=[str(i) for i in docs_batch.id])

def ELastic_upload(documents,index_name_write,  es_connection, batch_size=100):
    num_docs = len(documents)
    num_batches = (num_docs + batch_size - 1) // batch_size

    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, num_docs)
        docs_batch = documents.iloc[start_idx:end_idx]

        retry_count = 0
        while retry_count < 4:  # Retry up to 3 times
            try:
                upload_batch(docs_batch, index_name_write, es_connection)
                print(f"Uploaded batch {i+1}/{num_batches}")
                time.sleep(30)
                break  # Exit retry loop if upload is successful
            except Exception as e:
                retry_count += 1
                print(f"Connection timed out for batch {i+1}/{num_batches}. Retrying... (Attempt {retry_count}/3)")
                if "Model [.elser_model_1] must be deployed to use." in str(e):
                    print("Model must be deployed. Trying to deploy now...")
                    create_and_deploy_model(es_connection)
                    print("Retry uploading batch...")
                elif "inference process queue is full." in str(e):
                    print("Inference process queue is full. Waiting for 30 seconds before retrying...")
                    time.sleep(30)  # Wait for the queue to clear
                else:
                    print("Error: ", e)

    print("Upload complete.")
    
    
def get_credentials():
	return {
		 "url" : "https://us-south.ml.cloud.ibm.com",
		"apikey" : "idQYAuBI1oahMyhmK52vlG-eNHMsFyF8yCaQWk0_yD0o"
    }
 
 
def send_to_watsonxai (prompt , model_id = "meta-llama/llama-3-70b-instruct",max_new_tokens = 4096):
    parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": max_new_tokens,
    "repetition_penalty": 1,
    "temperature":0.3,
    "random_seed":42,
    "stop_sequences": ["```", "}"]
    }
    #project_id = "49246c83-5a8e-4805-a745-e3b6ac453c21"
    project_id= "e8fff495-cc9f-4285-ad88-7da5faf37ed5"
    model = Model(
	model_id = model_id,
	params = parameters,
	credentials = get_credentials(),
	project_id = project_id
	)
    generated_response = model.generate_text(prompt)
    return generated_response
    

def final_6(obligation, contract_doc):
  template = template = """
Instructions:
a) You are an legal practitioner developed to analyze if the given contract document is in compliance with the  obligation or whether the given contract document is in violation with the obligation
b) Do not assume anything on your own; consider the input contract document and obligation given to you as the only inputs.
c) If the contract document is in violation with the obligation, then print precise justification or explanation of why the contract document is in violation with the obligation and missing elements.
d) print only justification and missing elements, do no print input obligation, do not print contract document
Print the output using the below JSON format. Print strings in single quotation inside the JSON.
JSON format:
{{
    "Compliance / Violation": "Print whether the contract document in compliance with the obligation or not",
    "Justification": "If contract document is in violation with the obligation, Print summarised justification in couple of sentences. keep it precise and short."
}}
Obligation: {}
Contract Document:{}
Output: 

"""

   # Format the template with the obligation and contract document content
  prompt_json = template.format(obligation, contract_doc)
#   print(prompt_json)
  # Call the Watson XAI API or your preferred text analysis tool
  temp_json = send_to_watsonxai(prompt_json)
  print("Received JSON from Watson XAI:")
  print(temp_json)
  
  return temp_json# Debugging statement



def search_query(contract_data,index_name,obligations_queries,es_connection,output):
    
    for obligation in obligations_queries:
        print("Obligation: ", obligation)
        print("#########################")
        relevant_contract_snippets = es_connection.search(index=index_name, body={
            "query": {
                "match": {
                    "text":obligation
                }
            },
            "sort": [
                {"_score": {"order": "desc"}}
            ],
            "size": 5  # To limit the results to top 5
        })
    
        # for hit in relevant_contract_snippets["hits"]["hits"]:
        #     # print(f"contract doc: {hit['_source']['text']}")
        #     # print(f"Score: {hit['_score']}")
        #     hit_score = 
        rel_snippets = [{"snippet":hit['_source']['text'], "score":hit['_score']} for hit in relevant_contract_snippets["hits"]["hits"] if hit['_score']> 50.00]
            # print("####################################################")
            
            # if hit_score> 0.50:
        wx_output= [{"wxd_snippet":rel_snippet['snippet'], "wxd_score":rel_snippet['score'], "wxai_output":final_6(obligation, rel_snippet['snippet'])} for rel_snippet in rel_snippets]
                
        output.append({"index":index_name,"obligation":obligation,
                                 "comparison": wx_output})
        
    return output
    



def main():
    es_connection=connection_toESDB()
    print("Connected to the Elastic search: ", es_connection.info())
    obligations_queries = get_policy_list() # TODO send the policy name and location
    contract_data = read_contract_documents() #TODO send the contract name and location
    output_json_list =[]
    
    for contract in contract_data:
        contract_id = contract['id']
        print(contract_id)
        contract_text = contract['text']

    
    for i,doc in enumerate(contract_data):
        print(doc['id'])
        create_index_and_embedings_contract_wxd(contract_data=doc['text'], es_connection=es_connection,documents=contract_data[i]['text'],index_name_write= doc['id'])
        #create_and_deploy_model(es_connection)
        batch_load_contract_data(documents=contract_data[i]['text'], index_name_write=doc['id'], es_connection=es_connection)
        output1= search_query(contract_data=doc['text'],index_name=doc['id'],obligations_queries=obligations_queries,es_connection=es_connection,output=output_json_list)
        output_file = open("legal_doc_comparison_output.json", "w")
        json.dump(output1, output_file)

        
if __name__ == "__main__":
    main()