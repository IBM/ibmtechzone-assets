from langchain_community.vectorstores import Milvus
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
import os
from pymilvus import Collection

from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)

COLLECTION_NAME = "COMPLETE_REQUIREMENTS_TABLE"
FILE_DIRECTORY = "../misc"
PARTITION_KEY_FIELD = "topic"

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
#connection_args={"host": "127.0.0.1", "port": "19530"}
username = os.getenv("MILVUS_USERNAME")
password = os.getenv("MILVUS_PASSWORD")
connection_args={"host": "158.175.181.135", "port":"8080", "secure":True, "server_pem_path":"cert.pem","server_name":"localhost","user":username,"password":password}                     

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

def process_text_files(file_dict):
    file_info_dict = []
    for key,value in file_dict.items():
        with open(os.path.join(FILE_DIRECTORY, value),"r") as file:
            #print("Reading file ",value)
            content  = file.read()
            file_info_dict.append({"file_name":value.split('.')[0], "topic": key, "content":content})
            file.close()
    return file_info_dict
         
def get_text_chunks(text, file_name, topic):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    doc = [Document(page_content=x, metadata={"file_name": file_name, "topic": topic}) for x in text_splitter.split_text(text)]
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


def get_similar_text(query, item_count, filter_value):
    subsystem_texts = ""
    vector_db = Milvus(
                embeddings,
                connection_args=connection_args,
                collection_name=COLLECTION_NAME,
        )
    docs = vector_db.similarity_search(query,k=item_count, expr="topic like '"+filter_value+"'")
    cnt = 1
    for doc in docs:
        subsystem_texts = (os.linesep).join([subsystem_texts, "CHILD CONTEXT "+str(cnt)+" : ", doc.page_content, os.linesep])
        cnt = cnt+1
    print(subsystem_texts)
    return subsystem_texts

#get_similar_text("The surface of automatic gates shall be round chamfering for passenger safety.To ensure",2,"AUTOMATIC FARE COLLECTION")

