import os
import json
from langchain_milvus.vectorstores import Milvus
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
load_dotenv()

MILVUS_HOST = os.getenv("milvus_host")
MILVUS_PORT = os.getenv("milvus_port")
MILVUS_SECURE = os.getenv("milvus_secure")
MILVUS_SERVER_PEM_PATH = os.getenv("milvus_server_pem_path")
MILVUS_SERVER_NAME = os.getenv("milvus_server_name")
MILVUS_USER = os.getenv("milvus_user")
MILVUS_PASSWORD = os.getenv("milvus_password")

MILVUS_SECURE = True if MILVUS_SECURE.lower() == 'true' else False

MILVUS_CONFIG = {
    "host": MILVUS_HOST,
    "port": MILVUS_PORT,
    "secure": MILVUS_SECURE,
    "server_pem_path": MILVUS_SERVER_PEM_PATH,
    "server_name": MILVUS_SERVER_NAME,
    "user": MILVUS_USER,
    "password": MILVUS_PASSWORD
}

class MilvusRetriever:
    def __init__(self, embeddings_model_name="mixedbread-ai/mxbai-embed-large-v1", 
                 collection_name="collection_adl", connection_args=MILVUS_CONFIG):
        model_kwargs = {'device': 'cpu'}
        embeddings_model = HuggingFaceEmbeddings(
            model_name=embeddings_model_name,
            model_kwargs=model_kwargs
        )
        self._vector_db = Milvus(
            embeddings_model,
            connection_args=connection_args,
            collection_name=collection_name,
            auto_id=True
        )

    def add_documents(self, docs):
        doc_ids = self._vector_db.add_documents(docs)
        return doc_ids
    
    def get_relevant_docs(self, query, k=4, filename=""):
        if filename:
            relevant_docs = self._vector_db.similarity_search(query, k=k, expr=f'filename=="{filename}"')
        else:
            relevant_docs = self._vector_db.similarity_search(query, k=k)
        return relevant_docs
    
    def get_relevant_docs_async(self, query, k=4, filename=""):
        if filename:
            relevant_docs = self._vector_db.asimilarity_search(query, k=k, expr=f'filename=="{filename}"')
        else:
            relevant_docs = self._vector_db.asimilarity_search(query, k=k)
        return relevant_docs