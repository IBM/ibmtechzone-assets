#Importing the librarues
import pandas as pd
import os
import copy
import re
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from langchain.text_splitter import RecursiveCharacterTextSplitter,CharacterTextSplitter
from langchain.vectorstores.elasticsearch import ElasticsearchStore
from langchain.chains import RetrievalQA
from elasticsearch.helpers import scan, bulk
from tqdm import tqdm
from dotenv import load_dotenv
from getpass import getpass
import time
import warnings
from elasticsearch import Elasticsearch
import json
from sentence_transformers import SentenceTransformer

#removing the warnings
warnings.filterwarnings("ignore")

import os
username = os.environ["ELASTICSEARCH_USERNAME"]
password = os.environ["ELASTICSEARCH_PASSWORD"]
elasticsearch_url = os.environ["URL"]
entity = os.environ["entity_name"]
file_path = os.environ["excel_file_path"]

#Reading the excel file
df = pd.read_excel(file_path, sheet_name='Data')
df.head(2)

df.shape

# Convert all values to lowercase
df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)

column_names = df.columns

# Function to convert row to sentence
def row_to_sentence(row):
    sentence_parts = [f"{col} is {row[col]}" for col in row.index]
    sentence = ", ".join(sentence_parts)
    return sentence

# Iterate through each row and convert to sentence
sentences = []
for index, row in df.iterrows():
    sentence = row_to_sentence(row)
    sentences.append(sentence)

# Print the sentences
for sentence in sentences:
    print(sentence)

# Create a DataFrame from the sentences list
sentences_df = pd.DataFrame(sentences, columns=['Sentences'])

# Print the DataFrame
print(sentences_df.head())

#sentences_df.to_csv(path + "/sentences_df.csv", index=False)


def connedction_toESDB():
    #elasticsearch_url = "https://ef1d6d84-c48c-4f0e-8272-0909a6ef9774.d7deeff0d58745aba57fa5c84685d5b4.databases.appdomain.cloud:32707"
    #username = os.environ.get('ELASTICSEARCH_USERNAME')
    #password= os.environ.get('ELASTICSEARCH_PASSWORD')
    cert_path = 'certificates'
    es_connection = Elasticsearch(
        elasticsearch_url,
        ca_certs=cert_path,
        verify_certs=False, ##added , was getting failed while verifying the certifcate
        basic_auth=(username, password))
    return es_connection

es=connedction_toESDB()
#es.info()

df = sentences_df

model = SentenceTransformer("all-MiniLM-L6-v2")
es.indices.delete(index="atos_bcode_excel_test", ignore_unavailable=True)

from sentence_transformers import SentenceTransformer
s_messages = df["Sentences"]

# Step 2: Format data for Elasticsearch
documents = [{"Sentences": msg} for msg in s_messages]

# Step 3: Create embeddings for log data
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(s_messages.tolist())

# Generate embeddings for each log message
embeddings = model.encode(df["Sentences"].tolist())


index_body = {
  "mappings": {
    "properties": {
      "Sentences": {"type": "text"},
      "embedding": {"type": "dense_vector", 
                    "dims": model.get_sentence_embedding_dimension(), 
                    "index": True,
                    "similarity": "cosine"
                   }  
                    # Add similarity property for ELSA
    }
  }
}

index_name = 'bcode_excel_test'

# Create the index if it doesn't exist
if not es.indices.exists(index=index_name):
  es.indices.create(index=index_name, body=index_body)

# Add data to the index with embeddings
for i, row in df.iterrows():
  doc = {
      "Sentences": row["Sentences"],
      "embedding": embeddings[i].tolist()  # Convert embedding to a list
  }

  #Ingest data
  es.index(index=index_name, id=i, body=doc)

# Load SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define your search function to accept parameters
def search(data_str, index_name, list_1):
    data = json.loads(data_str)
    entity_term = data['entity']
    print("entity term : ")
    print(entity_term)

    if not entity_term:
        return {'error': 'Query parameter is required'}, 400

    entity_term = entity_term.lower()

    try:
        query = {
            'query': {
                'match_phrase': {
                    'Sentences': 'Master Sub-Category is ' + entity_term
                }
            },
            'size': 50
        }

        response = es.search(index=index_name, body=query)
        hits = response['hits']['hits']

        if len(hits) == 0:
            if entity_term in list_1:
                query['query']['match_phrase']['Sentences'] = 'Purchasing category is ' + entity_term
            else:
                query['query']['match_phrase']['Sentences'] = 'Purchasing sub-category description Material Group is ' + entity_term

            response = es.search(index=index_name, body=query)
            hits = response['hits']['hits']

        results = [{'_source': hit['_source']['Sentences']} for hit in hits]

        pattern = r'([\w\s/.+-]+) is ((?:[\w\s().+\n/-]+(?:\s[\w\s().+\n/-]+)*))[,|$]'
        
        return results

    except Exception as e:
        return {'error': str(e)}, 500

# Define the parameters
data = {
    "entity": entity_name
}
data_str = json.dumps(data)
#index_name = 'your_index_name'  # Replace with your actual index name
list_1 = ['list', 'of', 'entities']  # Replace with your actual list

# Call the search function directly
results = search(data_str, index_name, list_1)
print(results)


