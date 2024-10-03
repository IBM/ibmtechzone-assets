from fastapi import FastAPI, HTTPException
import pandas as pd
import copy
import os
import re
from elasticsearch import Elasticsearch, exceptions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.elasticsearch import ElasticsearchStore
from llama_index.core import SimpleDirectoryReader
from dotenv import load_dotenv
from tqdm import tqdm
import time
from elasticsearch.exceptions import ConnectionTimeout
import ssl
import ibm_boto3
from ibm_botocore.client import Config
import logging

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to establish connection to Elasticsearch
def get_connection():
    # Load environment variables for IBM COS
    COS_ENDPOINT = os.environ["COS_ENDPOINT"]
    COS_API_KEY_ID = os.environ["COS_API_KEY_ID"]
    COS_INSTANCE_CRN = os.environ["COS_INSTANCE_CRN"]
    COS_BUCKET_NAME = os.environ["COS_BUCKET_NAME"]
    COS_FILE_KEY = os.environ["COS_FILE_KEY"]

#     # Create the IBM COS client
#     cos_client = ibm_boto3.client(
#         "s3",
#         ibm_api_key_id=COS_API_KEY_ID,
#         ibm_service_instance_id=COS_INSTANCE_CRN,
#         config=Config(signature_version="oauth"),
#         endpoint_url=COS_ENDPOINT
#     )

#     # Read .crt file content from COS
#     crt_content = read_crt_file_from_cos(cos_client, COS_BUCKET_NAME, COS_FILE_KEY)
#     logger.info('Before Certificate reading')
#     crt_content = os.environ["wxd_certificate"]

#     # Create SSL context for Elasticsearch connection using the .crt content
#     context = ssl.create_default_context(cadata=crt_content)
#     logger.info('After Certificate reading')
#     es_connection = Elasticsearch([os.environ["es_endpoint"]], ssl_context=context)
    # By pass the SSL auth.
    es_connection = Elasticsearch([os.environ["es_endpoint"]], verify_certs=False,http_auth=None)#ssl_context=context)

    # Check if the connection to Elasticsearch is successful
    if es_connection.ping():
        logger.info('Connection Successful')
    else:
        logger.error("Connection Failed")
    return es_connection

# Function to create and deploy the embedding model on Elasticsearch
def create_and_deploy_model(es_connection, es_model_id):
    try:
        # Delete existing model if it exists
        es_connection.ml.delete_trained_model(model_id=es_model_id, force=True)
        logger.info("Model deleted successfully, We will proceed with creating one")
    except exceptions.NotFoundError:
        logger.info("Model doesn't exist, but We will proceed with creating one")

    # Create a new model
    es_connection.ml.put_trained_model(
        model_id=es_model_id, input={"field_names": ["text_field"]}
    )

    # Wait for the model to be fully defined
    while True:
        status = es_connection.ml.get_trained_models(
            model_id=es_model_id, include="definition_status"
        )

        if status["trained_model_configs"][0]["fully_defined"]:
            logger.info("ELSER Model is downloaded and ready to be deployed.")
            break
        time.sleep(5)

    # Start model deployment
    es_connection.ml.start_trained_model_deployment(
        model_id=es_model_id, number_of_allocations=1, wait_for="starting"
    )

    # Wait for the deployment to start
    while True:
        status = es_connection.ml.get_trained_models_stats(
            model_id=es_model_id,
        )
        if status["trained_model_stats"][0]["deployment_stats"]["state"] == "started":
            logger.info("ELSER Model has been successfully deployed.")
            break
        time.sleep(2)

# Function to process documents based on chunk size and prepare the data
def process_local_docs(chunk_size, chunk_overlap, index_name):
    # Load raw documents from the specified directory
    raw_documents = SimpleDirectoryReader(
        os.environ["file_path_doc"], recursive=True).load_data()

    # Initialize text splitter with specified chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
    )

    actions = []
    idx = 0

    # Split each document into chunks
    for doc in tqdm(raw_documents):
        text = doc.text
        text = ' '.join(text.split())
        text = re.sub(r'\s+', ' ', text)
        text_chunks = text_splitter.split_text(text)

        idx += 1
        temp = 0
        for chunk in text_chunks:
            new_doc = copy.deepcopy(doc)
            temp += 1
            new_doc.text = chunk

            action = {
                "index": index_name,
                "id": new_doc.metadata['file_name'] + "_" + new_doc.metadata['page_label'] + "." + str(temp),
                "title": new_doc.metadata['file_name'],
                "page_number": new_doc.metadata['page_label'],
                "source_reference": os.environ[new_doc.metadata['file_name'].replace(" ", "-")],
                "description": "Defense Data",
                "body_content_field": "",
                "text": chunk
            }
            actions.append(action)
    
    # Convert actions list to DataFrame
    documents2 = pd.DataFrame(actions)
    return documents2

# Function to upload processed data into Elasticsearch
def upload_batch(es_connection, docs_batch, index, es_model_id):
    # Create Elasticsearch vector store
    vector_store = ElasticsearchStore(es_connection=es_connection,
                                      index_name=index,
                                      strategy=ElasticsearchStore.SparseVectorRetrievalStrategy(model_id=es_model_id))
    
    # Prepare metadata for each document chunk
    metadata = []
    for file_name, page_num, source_ref in zip(docs_batch.title.tolist(), docs_batch.page_number.tolist(), docs_batch.source_reference.tolist()):
        metadata.append({"file_name": file_name, "page_number": page_num, 'source_reference': source_ref})

    # Upload document chunks to Elasticsearch
    _ = vector_store.add_texts(texts=docs_batch.text.tolist(),
                              metadatas=metadata,
                              index_name=index,
                              request_timeout=10000,
                              ids=[str(i) for i in docs_batch.id])

# Function to upload documents to Elasticsearch in batches
def elastic_upload(es_connection, documents, batch_size, index, es_model_id):
    num_docs = len(documents)
    num_batches = (num_docs + batch_size - 1) // batch_size

    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, num_docs)
        docs_batch = documents.iloc[start_idx:end_idx]
        retry_count = 0

        # Retry logic for batch upload in case of connection timeouts
        while retry_count < 4:
            try:
                upload_batch(es_connection, docs_batch, index, es_model_id)
                logger.info(f"Uploaded batch {i+1}/{num_batches}")
                time.sleep(30)
                break
            except ConnectionTimeout as e:
                retry_count += 1
                logger.warning(f"Connection timed out for batch {i+1}/{num_batches}. Retrying... (Attempt {retry_count}/3)")
                time.sleep(15)
                if f"Model [{es_model_id}] must be deployed to use." in str(e):
                    logger.info("Model must be deployed. Trying to deploy now...")
                    logger.info("Retry uploading batch...")
                elif "inference process queue is full." in str(e):
                    logger.info("Inference process queue is full. Waiting for 30 seconds before retrying...")
                    time.sleep(30)
                else:
                    logger.error(f"Error: {e}")

    logger.info("Upload complete.")

# Function to close the Elasticsearch connection
def cleanup(es_connection):
    es_connection.close()

# API endpoint to upload documents
@app.post("/ingest-documents/")
async def upload_documents(index_name: str, chunk_size: int, overlap_size: int, es_model_id: str, model_deploy: bool):
    logger.info("Starting document ingestion...")
    # Establish Elasticsearch connection
    es_connection = get_connection()
    if model_deploy:
        # Create and deploy model if required
        create_and_deploy_model(es_connection, es_model_id)
    
    # Process documents and prepare data
    docs_final = process_local_docs(chunk_size, overlap_size, index_name).copy(deep=True)

    # Delete existing index if required
    if os.environ["index_update"].lower() == "false":
        if es_connection.indices.exists(index=index_name):
            es_connection.indices.delete(index=index_name)
    
    # Upload documents to Elasticsearch
    elastic_upload(es_connection, docs_final, 50, index_name, es_model_id)

    logger.info("Document ingestion completed.")
    return {"message": "Documents are being processed and uploaded."}

# API endpoint to search documents
@app.get("/search/")
async def search_documents(search_query: str, index_name: str, es_model_id: str):
    logger.info("Starting document search...")
    try:
        # Establish Elasticsearch connection
        es_connection = get_connection()
        
        # Perform search on Elasticsearch
        search_results = es_connection.search(index=index_name, body={
            "query": {
                "text_expansion": {
                    "vector.tokens": {
                        "model_id": es_model_id,
                        "model_text": search_query
                    }
                }
            },
            "sort": [
                {"_score": {"order": "desc"}}
            ]
        })
        results = []
        # Parse search results
        for hit in search_results["hits"]["hits"]:
            result = {
                "text": hit["_source"]["text"],
                "score": hit["_score"],
                "metadata": hit["_source"]["metadata"],
                "index": hit["_index"]
            }
            results.append(result)

        # Close Elasticsearch connection
        cleanup(es_connection)
        logger.info("Document search completed.")
        return {"results": results}
    except Exception as ex:
        logger.error(f"Error while fetching data from Elastic DB: {ex}")
        raise HTTPException(status_code=500, detail="Error while fetching data from Elastic DB." + str(ex))

# Run the FastAPI app with Uvicorn
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)