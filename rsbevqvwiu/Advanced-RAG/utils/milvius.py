import re, os
from sentence_transformers import SentenceTransformer
# from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from pymilvus import (connections, utility, FieldSchema, CollectionSchema, DataType, Collection, )
from dotenv import load_dotenv


CERTIFICATE_PATH = os.getenv("CERTIFICATE_PATH")

top_K = 5


class VectorDB:
    def __init__(self):
        load_dotenv()
        self.milvus_host = os.getenv("MILVUS_HOST", None)
        self.milvus_port = os.getenv("MILVUS_PORT", None)
        self.milvus_user = os.getenv("MILVUS_USER", None)
        self.milvus_password = os.getenv("MILVUS_PASSWORD", None)
        self.milvus_server = os.getenv("MILVUS_SERVER_NAME", None)

        # make connection with milvus db
        connections.connect(host=self.milvus_host,
                            port=self.milvus_port,
                            secure=True,
                            server_pem_path=CERTIFICATE_PATH,
                            server_name=self.milvus_server,
                            user=self.milvus_user,
                            password=self.milvus_password)

    def get_collection(self, name):
        collection = Collection(name)
        return collection
    
    def create_collection(self, name, dimension):
        # Define collection schema
        schema = CollectionSchema(
            fields=[
                FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=dimension, is_primary=True)
            ],
            description="Collection for storing sentence embeddings"
        )
        collection = Collection(name=name, schema=schema)
        return collection

    def insert(self, collection_name, embeddings):
        # Insert embeddings into Milvus collection
        collection = Collection(name=collection_name)
        collection.insert(data=embeddings)

    def query_milvus(self, query, collection_name):
        # Load the collection:
        collection = Collection(name=collection_name)
        # Load the collection
        collection.load()
        # Vectorize the query for the latest war updates
        embedding_model = SentenceTransformer('bert-base-nli-mean-tokens')
        query_embeddings = embedding_model.encode(str(query))  # Encoding the whole query
        output_fields = ['chunks', 'chunk_id', "url"]
        # Search parameters
        search_params = {"metric_type": "L2", "params": {"nprobe": 5}}
        # Perform the search
        results = collection.search(
            data=[query_embeddings],
            anns_field='embeddings',
            param=search_params,
            limit=5,
            expr=None,
            output_fields=output_fields
        )

        return results