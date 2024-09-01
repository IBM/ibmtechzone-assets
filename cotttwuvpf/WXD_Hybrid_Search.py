# Import necessary libraries.
import pandas as pd
import copy
import os
import re
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch, exceptions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.elasticsearch import ElasticsearchStore
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from elasticsearch.helpers import scan
from tqdm import tqdm
from elasticsearch.exceptions import ConnectionTimeout
import time
import ssl
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ibm_watsonx_ai.foundation_models import Model
import json
import os, time
from elasticsearch import helpers
import urllib3
import datetime
from llama_index.core.node_parser import SentenceSplitter
from elasticsearch.helpers import BulkIndexError


def load_text_parser():
    return SentenceSplitter(
        chunk_size=500,
        chunk_overlap=10,
        # separator=" ",
    )
load_dotenv()
index_name =os.environ["index_name_new"]
ingest_pipeline_id=os.environ["index_hybrid_pipeline"]


file_path_doc = os.environ["file_path_doc"]

# Get Elastic search end point.
es_endpoint = os.environ["es_endpoint"]

# Get Elastic search DB certificate path.
es_cert_path = os.environ["es_cert_path"]
es_username = os.environ["username"]
es_pwd=os.environ["password"]

elser_model_name =os.environ["elser_model_name"]
dense_model_name =os.environ["dense_model_name"]
dense_dim =int(os.environ["dense_dim"])

def setup_elasticsearch():
    # SSL context for Elasticsearch connection
    context = ssl.create_default_context(cafile=es_cert_path)

    # Connect to the Elasticsearch server
    es_connection = Elasticsearch([es_endpoint], ssl_context=context)

    # Check connection status
    if es_connection.ping():
        print('Connection Successful')
    else:
        print("Connection Failed")
    return es_connection

def deploy_model(es_connection,es_model_id):

    try:
        es_connection.ml.delete_trained_model(model_id=es_model_id, force=True)
        print("Model deleted successfully, proceeding with creation")
    except exceptions.NotFoundError:
        print("Model doesn't exist, proceeding with creation")

    # Create the embedded (ELSER) model configuration.
    es_connection.ml.put_trained_model(
        model_id=es_model_id, input={"field_names": ["text_field"]}
    )

    # Wait until the model is fully defined and deployed
    while True:
        status = es_connection.ml.get_trained_models(
            model_id=es_model_id, include="definition_status"
        )
        if status["trained_model_configs"][0]["fully_defined"]:
            print("ELSER Model is downloaded and ready to be deployed.")
            break
        time.sleep(5)

    # Start trained model deployment if not already deployed
    es_connection.ml.start_trained_model_deployment(
        model_id=es_model_id, number_of_allocations=1, wait_for="starting"
    )

    while True:
        status = es_connection.ml.get_trained_models_stats(
            model_id=es_model_id,
        )
        if status["trained_model_stats"][0]["deployment_stats"]["state"] == "started":
            print("ELSER Model has been successfully deployed.")
            break
        print("ELSER Model is currently being deployed.")
        time.sleep(2)

def convert_date(from_m_d_yy):
    return datetime.datetime.strptime(from_m_d_yy,
                                      "%m/%d/%y").strftime("%Y/%m/%d")

def process_chunks(csv_file):
    text_parser = load_text_parser()
    documents=[]
    csv_data = pd.read_csv(csv_file)
    text_parser = load_text_parser()
    for i, s in csv_data.iterrows():
        title = s["title"]
        text = s["text"]
        pub_date = convert_date(s["reg_date"])
        text_chunks = text_parser.split_text(text)
        for i_c, chunk in enumerate(text_chunks):
            doc = {
                "id": s["doc_id"] + "_" + str(i_c),
                "text": title + "\n" + chunk,
                "original_text": chunk,
                "publication_date": pub_date,
                "url": s["source_URL"],
            }
            # print(doc)
            yield {
                "_index": index_name,
                "_id": doc["id"],
                'pipeline': ingest_pipeline_id,
                "_source": doc
            }  
             # documents.append({
                # "_index": index_name,
                # "_id": doc["id"],
                # 'pipeline': ingest_pipeline_id_news,
                # "_source": doc
                # })

def create_hybrid_pipeline(ingest_pipeline_id, client):    
    res=client.ingest.put_pipeline(
        id=ingest_pipeline_id,
        description="Ingest pipeline for Elser encoding and dense encoding",
        processors=[
            {
                "inference": {
                    "model_id": elser_model_name,
                    "input_output": [
                        {"input_field": "text",
                         "output_field": "text_sparse_embedding"}
                    ],
                },
            },
            {
                "inference": {
                    "model_id": dense_model_name,
                    "input_output": {
                        "input_field": "text",
                        "output_field": "text_dense_embedding",
                    },
                }
            },
             
        ],
        
    )
    print(res)


def create_hybrid_index(index_name, client):
    #to delete the index already present and create new 
    client.indices.delete(index=index_name, ignore_unavailable=True)
    res=client.indices.create(
        index=index_name,
        settings={},
        mappings={
            "properties": {
                "text": {"type": "text"},
                "text_sparse_embedding": {"type": "sparse_vector"},
                "text_dense_embedding": {
                    "type": "dense_vector",
                    "dims": dense_dim,
                    "similarity": "cosine",
                }
            }
        },
    )
    print(res)



def ingest_parallel_bulk(es_connection, chunks, chunk_size):
    start_ingest_t = time.time()
    try:
        for success, info in helpers.parallel_bulk(es_connection, chunks,
                                                thread_count=8,
                                                chunk_size=chunk_size,
                                                request_timeout=5000):
            print("documents uploaded")
            if not success:
                print('A document failed:', info)
    except BulkIndexError as e:
        # Log or print the detailed errors
        print(f"Bulk indexing error: {len(e.errors)} documents failed to index.")
        for error in e.errors:
            print(error)
    print(f"Ingestion completed: {time.time() - start_ingest_t}s")

def search_elser(query, client, index_names, n):
    return client.search(
        index=index_names,
        size=n,
        query={
            "text_expansion": {
                "text_sparse_embedding": {
                    "model_id": elser_model_name,
                    "model_text": query,
                }
            }
        }
    )

def search_hybrid(query, client, index_names, n):
    return client.search(
        index=index_names,
        size=n,
        query={
            "text_expansion": {
                "text_sparse_embedding": {
                    "model_id": elser_model_name,
                    "model_text": query,
                }
            }

        },
        knn={
            "field": "text_dense_embedding",
            "query_vector_builder": {
                "text_embedding": {
                    "model_id": dense_model_name,
                    "model_text": query,
                }
            },
            "k": 10,
            "num_candidates": 100
        },
        rank={"rrf": {}},
    )


if __name__ == "__main__":

    es_connection=setup_elasticsearch()


    create_hybrid_index(index_name, es_connection)
    create_hybrid_pipeline(ingest_pipeline_id, es_connection)
    print("created index and pipeline")
    chunks=process_chunks(file_path_doc)
    print(type(chunks))
    ingest_parallel_bulk(es_connection, chunks, chunk_size=10)
   


    
   