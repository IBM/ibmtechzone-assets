# Import necessary libraries.
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
from elasticsearch.client import IndicesClient
import ssl

# Load .env file.
load_dotenv()

# Set index name.
index_name_write = 'cfsg'

# Set model id which will used for embeddings.
es_model_id = ".elser_model_1"

# Set chunk and overlap size.
chunk_size = 150
chunk_overlap = 10

# Define Elasticsearch settings
# elasticsearch_url = os.getenv("es_endpoint", None)
# username = os.getenv("username", None)
# password = os.getenv("password", None)

# Get the source document file paths.
file_path_doc = os.environ["file_path_doc"]

# Get Elastic search end point.
es_endpoint = os.environ["es_endpoint"]

# Get Elsatic search DB certifcate path.
es_cert_path = os.environ["es_cert_path"]

# Get the flag to check whether you want to update the index or delet and create new index and default values will be false.false represent delete the existing index and create new one.
index_update = os.environ["index_update"]


# Get the Elastic DB connection object.
def get_connection():

    # Set user name and password, certificate path to Elastic DB.
    # es_connection = Elasticsearch(
    # elasticsearch_url,
    # ca_certs=cert_path,
    # basic_auth=(username, password))

    # SSL context for Elasticsearch connection
    context = ssl.create_default_context(cafile=es_cert_path)

    # Connect to the Elasticsearch server
    es_connection = Elasticsearch([es_endpoint], ssl_context=context)

    # Check whether you got connection object from Elastic DB or not ?
    if es_connection.ping():
        print('Connection Successful')
    else:
        print("Connection Failed")
    return es_connection


# Create the embedding model and deploy it.
def create_and_deploy_model(es_connection):

    # Delete already created and deployed model.
    try:
        es_connection.ml.delete_trained_model(model_id=es_model_id, force=True)
        print("Model deleted successfully, We will proceed with creating one")
    except exceptions.NotFoundError:
        print("Model doesn't exist, but We will proceed with creating one")

    # Creates the embedded(ELSER) model configuration. Automatically downloads the model if it doesn't exist.
    es_connection.ml.put_trained_model(
        model_id=es_model_id, input={"field_names": ["text_field"]}
    )

    # Keep a loop to create and deploy the embedded model(exit the loop when the process successs).  
    while True:
        status = es_connection.ml.get_trained_models(
            model_id=es_model_id, include="definition_status"
        )

        if status["trained_model_configs"][0]["fully_defined"]:
            print("ELSER Model is downloaded and ready to be deployed.")
            break
        else:
            # print("ELSER Model is downloaded but not ready to be deployed.")
            pass
        time.sleep(5)

    # Start trained model deployment if not already deployed
    es_connection.ml.start_trained_model_deployment(
        model_id=es_model_id, number_of_allocations=1, wait_for="starting"
    )

    # Get the status of deployed embedded model.
    while True:
        status = es_connection.ml.get_trained_models_stats(
            model_id=es_model_id,
        )
        if status["trained_model_stats"][0]["deployment_stats"]["state"] == "started":
            print("ELSER Model has been successfully deployed.")
            break
        else:
            print("ELSER Model is currently being deployed.")
        time.sleep(2)


# Process the documents based on chunk size/passages/line..etc and prepare the data in the form of watsonx discovery.
def process_local_docs():

    # Read documents from local directory(If the directory has multiple files with different format/extension then also reader will pick it up and if needed install the read library like doctotext,pdf2text..etc)
    raw_documents = SimpleDirectoryReader(
        file_path_doc, recursive=True).load_data()

    # Process the document based on chunk size.
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(  
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
    )

    # '#' will chunk the PDF page by page.
    # text_splitter = RecursiveCharacterTextSplitter("#")

    actions = []
    idx = 0
   # print('Raw Documents : ',raw_documents)

    # Process the document page by page(SimpleDirectoryReader will read the docuemnts page by page).
    for doc in tqdm(raw_documents):
        
        # Get the text from the document.
        text = doc.text

        # Process the text.
        text = ' '.join(text.split())
        text = re.sub(r'\s+', ' ', text)
        text_chunks = text_splitter.split_text(text)

        # Prepare the page number.
        idx += 1
        temp = 0
        # Process the text chunks(page by page or passage by pasage or chunk size...etc)
        for chunk in text_chunks:
            new_doc = copy.deepcopy(doc)
            temp += 1
            #print('Doc Name :',new_doc.metadata['file_name'])

            # Copy the original document text
            new_doc.text = chunk  # Replace the body content with the chunk
            # new_doc["_source"]["text"] = chunk

            # Prepare the data in Json format which supports watsonx discovery.
            action = {
                "index": index_name_write,
                "id": new_doc.metadata['file_name']+"_"+new_doc.metadata['page_label']+"."+str(temp), # if you don't set id value then watsonx discovery generated unique GUID for each file/chunk.
                "title": new_doc.metadata['file_name'],
                "page_number": new_doc.metadata['page_label'],
                "source_reference": os.environ[new_doc.metadata['file_name'].replace(" ","-")],
                "description": "Defense Data",
                "body_content_field":"",
                "text": chunk
            }
            actions.append(action)
    
    # Prepare a data frame using json/dictionary data.
    documents2 = pd.DataFrame(actions)

    return documents2

# Upload processed data into watsonx discovery.
def upload_batch(es_connection, docs_batch, index):

    # Get the vector store object for storing the data.
    vector_store = ElasticsearchStore(es_connection=es_connection,
                                      index_name=index,
                                      strategy=ElasticsearchStore.SparseVectorRetrievalStrategy(model_id=es_model_id))
    
    # Create a list to store metadata like file name, paege number, file reference link...etc
    metadata=list()

    # Prepare metadata for chunks.
    for file_name,page_num,source_ref in zip(docs_batch.title.tolist(),docs_batch.page_number.tolist(),docs_batch.source_reference.tolist()):
        metadata.append({"file_name":file_name,"page_number":page_num,'source_reference':source_ref})

    # Upload embedding into Vector store.
    _ = vector_store.add_texts(texts=docs_batch.text.tolist(),
                              metadatas=metadata,
                               index_name=index_name_write,
                               request_timeout=10000,
                               ids=[str(i) for i in docs_batch.id])


# Uplaod data into elsatic DB.
def elastic_upload(es_connection, documents, batch_size=100):

    # Get the number of document size.
    num_docs = len(documents)

    # Calculate the bath size for processing the documents.
    num_batches = (num_docs + batch_size - 1) // batch_size

    # Process the data batch by batch.
    for i in range(num_batches):

        # Prepare start index.
        start_idx = i * batch_size

        # Prepare end index.
        end_idx = min((i + 1) * batch_size, num_docs)

        # Get documents based on indexes.
        docs_batch = documents.iloc[start_idx:end_idx]

        #print(docs_batch)
        retry_count = 0

        # Retry up to 3 times to load the data into Elastic DB.
        while retry_count < 4:  
            try:
                upload_batch(es_connection, docs_batch, index_name_write)
                print(f"Uploaded batch {i+1}/{num_batches}")
                time.sleep(30)
                break  # Exit retry loop if upload is successful
            except ConnectionTimeout as e:
                retry_count += 1
                print(
                    f"Connection timed out for batch {i+1}/{num_batches}. Retrying... (Attempt {retry_count}/3)")
                time.sleep(15)
                if "Model [.elser_model_1] must be deployed to use." in str(e):
                    print("Model must be deployed. Trying to deploy now...")
                    # create_and_deploy_model(es_connection)
                    print("Retry uploading batch...")
                elif "inference process queue is full." in str(e):
                    print(
                        "Inference process queue is full. Waiting for 30 seconds before retrying...")
                    time.sleep(30)  # Wait for the queue to clear
                else:
                    print("Error: ", e)

    print("Upload complete.")


# Prepare Synonyms list in json format.
def get_synonyms_list():
    synonyms = {
        "analysis": {
            "filter": {
                "english_synonyms": {
                    "type": "synonym",
                    "synonyms": [
                                 "DPL => Defence Protected Laptop",
                                 "PED => Portable Electronic Device",
                                 "DSPF => Defence Security Principles Framework",
                                 "ADF => Australian Defence Force",
                                 "FVEY => Five Eyes",
                                 "PSPF => Protective Security Policy Framework",
                                 "CDF => Chief of the Defence Force",
                                 "DPN => Defence Protected Network",
                                 "CSO => Chief Security Officer",
                                 "DSC => Defence Security Committee",
                                 "EBC => Enterprise Business Committee",
                                 "CIOG => Chief Information Officer Group"
                    ]
                }
            },
            "analyzer": {
                "synonym_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["english_synonyms"]
                }
            }
        }
    }
    return synonyms


# Release Elastic DB conenction.
def cleanup(es_connection):
    es_connection.close()


# Read the documents, process it, upload them into WatsonX Discovery and get search result.
def main():

    # Get Elsatic DB connection.
    es_connection = get_connection()

    # If the embedded model is not deployed then enable below comment to deploy it(just enable only for the first time).
    create_and_deploy_model(es_connection)

    # Process the docuemnts.
    docs_final = process_local_docs().copy(deep=True)
    #print(docs_final)

    # If index_update is true then load the data into existing index else delete existing and create new one
    if index_update.lower()=="false":
        #Check whether the index is already present in the DB or not ?
        if es_connection.indices.exists(index=index_name_write):
            # If the index is already present then delete the existing index.
            es_connection.indices.delete(index=index_name_write)
        
    # Upload the processed documents.
    elastic_upload(es_connection, docs_final, batch_size=50)

    # Instantiate IndicesClient.
    indices_client = IndicesClient(es_connection)

    # Copy index name.
    index_name = index_name_write

    # Update the existing index setting file with the synonyms.
    indices_client.close(index=index_name)
    indices_client.put_settings(body=get_synonyms_list(), index=index_name)
    indices_client.open(index=index_name)

    # Search query.
    search_text = "What is DSPF"

    # Add Synonyms to search query(First it gets abbrivation value and then it does search).
    search_query = {
        "query": {
            "match": {
                "content": {
                    "query": search_text,
                    "analyzer": "synonym_analyzer"
                }
            }
        }
    }

    # Get result from WatsonX discovery for passed query.
    # search_results = es_connection.search(index=index_name, body=search_query)

    # Get results from WatsonX discovery for passed query.
    search_results = es_connection.search(index=index_name_write, body={
        # "query": {
        #     "match": {
        #         "text": "Can I use my personal device to access DREAMS from overseas?"
        #     }
        # },
        "query":{
      "text_expansion":{
         "vector.tokens":{ 
            "model_id":es_model_id,
            "model_text":"How does the use of generative AI align with CAFG's long-term growth strategy and innovation goals in the FinTech sector, and what does this mean for our future?"
         }
      }
   },
        "sort": [
            {"_score": {"order": "desc"}}
        ]
    })

   # print('Search Result Object : ',search_results)

    # Process the search result to display answer,score,metadata(File name, page number, soure reference link) and index name.
    for hit in search_results["hits"]["hits"]:
        print(f"Result: {hit['_source']['text']}")
        print(f"Score: {hit['_score']}")
        print(f"File Name: {hit['_source']['metadata']}")
        print(f"Index Name:",{hit['_index']})
        print("####################################################")

    # Close the Elastic DB connection.
    cleanup(es_connection)


# Start point.
if __name__ == '__main__':
    main()
