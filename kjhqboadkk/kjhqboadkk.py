from langchain_community.vectorstores import Milvus
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
import os
from pymilvus import Collection
import pandas as pd
import io
from bs4 import BeautifulSoup
import re

from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)

#COLLECTION_NAME = "TEST_CASES_TABLES"
COLLECTION_NAME = "TEST_CASES_DISCOVERY"
FILE_DIRECTORY = r"../test_preprocess/txt/"
DISCOVERY_FILE = r"../discovery_files/"
PARTITION_KEY_FIELD = "topic"

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
connection_args={"host": "127.0.0.1", "port": "19530"}

username = os.getenv("MILVUS_USERNAME")
password = os.getenv("MILVUS_PASSWORD")



index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128},
}


metadata_field_info = [
    AttributeInfo(
        name="file_name",
        description="name of file from which data is extracted",
        type="string",
    ),
    AttributeInfo(
        name="topic",
        description="the topic to which the text belongs",
        type="string",
    )
]

# process using Unstructured
def process_text_files(file_dict):
    file_info_dict = []
    for key,value in file_dict.items():
        with open(os.path.join(FILE_DIRECTORY, value),"r") as file:
            #print("Reading file ",value)
            content  = file.read()
            print(os.path.join(FILE_DIRECTORY, value))
            print(content)
            file_info_dict.append({"file_name":value.split('.')[0], "topic": key, "content":content})
            file.close()
    return file_info_dict

# process using Discovery
def process_text_files_discovery(file_dict):
    file_info_dict = []
    for key,value in file_dict.items():
        with open(os.path.join(FILE_DIRECTORY, value),"r") as file:
            #print("Reading file ",value)
            content  = file.read()
            print(os.path.join(FILE_DIRECTORY, value))
            print(content)
            file_info_dict.append({"file_name":value.split('.')[0], "topic": key, "content":content})
            file.close()
    return file_info_dict

def get_text_chunks(text, file_name, topic):
    doc = [Document(page_content=x+"</table>", metadata={"file_name": file_name, "topic": topic}) for x in text.split(r"</table>")]
    return doc

def get_milvus():
    milvus_db = Milvus(
            embedding_function=embeddings,
            connection_args=connection_args,
            collection_name=COLLECTION_NAME,
            partition_key_field=PARTITION_KEY_FIELD,
            index_params=index_params
            )
    return milvus_db

def add_to_vector_store(docs):
    try:
        vector_db = get_milvus()
        vector_store = vector_db.from_documents(
                docs,
                embedding = embeddings,
                collection_name = COLLECTION_NAME,
                connection_args = connection_args,
                partition_key_field="topic"
            )
    except Exception as e:
        print(f"Error storing data into Milvus: {e}")
        vector_db = None
    
    return vector_store


def get_similar_doc(query, item_count):
        vector_db = Milvus(
                embeddings,
                connection_args=connection_args,
                collection_name=COLLECTION_NAME
        )
        docs = vector_db.similarity_search(query, k=item_count)
        return docs

    
  """
  Here are the steps:
  
  step 1: Process your text file
  step 2: Add tabular chunks to the vector store
  step 3: Seach for similar tabular information based on provided inputs
  """