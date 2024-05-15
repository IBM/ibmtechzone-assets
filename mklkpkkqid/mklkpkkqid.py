import warnings
import nest_asyncio
from elasticsearch import Elasticsearch, AsyncElasticsearch
nest_asyncio.apply()
warnings.filterwarnings('ignore')
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os
from dotenv import load_dotenv
import logging
import time
from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

logging.basicConfig(level=logging.INFO)
load_dotenv()
#watsonx.ai
api_key = os.getenv("GENAI_KEY", None)
watsonx_url = os.getenv("WATSONX_URL", None)
watsonx_project_id = os.getenv("GENAI_PROJECT_ID", None)
#watson discovery
wd_project_id= os.getenv("WD_PROJECT_ID", None)
wd_api_key = os.getenv("WD_API_KEY", None)
eLaws_collection_id= os.getenv("ELAWS_COLLECTION_ID", None)
interpretations_collection_id= os.getenv("INTERPRETATIONS_COLLECTION_ID", None)
palm_collection_id= os.getenv("PALM_COLLECTION_ID", None)

wd_service_url = os.getenv("WD_SERVICE_URL", None)
#WatsonX discovery 
url = os.getenv("WXD_URL", None)
username= os.getenv("WXD_USERNAME", None)
password = os.getenv("WXD_PASSWORD", None)

#Regex helper function to extract version start and end dates from a string
import re
from datetime import datetime

def extract_dates(text):
    # Updated pattern to optionally match "to the eLaws currency date"
    pattern = r'(\w+\s\d{1,2},\s\d{4})\sto\s((\w+\s\d{1,2},\s\d{4})|the eLaws currency date)'
    match = re.search(pattern, text)
    if match:
        start_date = match.group(1)
        # If the end date matches a specific date, use it; otherwise, use "the eLaws currency date"
        end_date = match.group(2) if match.group(3) else "the eLaws currency date"
        # Adjusted print statement to accommodate for the potential absence of a specific end date
        #print(start_date + " to " + (end_date if end_date != "the eLaws currency date" else "the eLaws currency date"))
        # Convert to datetime objects
        start_date_obj = datetime.strptime(start_date, '%B %d, %Y')
        end_date_obj = datetime.strptime(end_date, '%B %d, %Y')
    
    # Format as "yyyy-MM-dd"
        start_date_formatted = start_date_obj.strftime('%Y-%m-%d')
        end_date_formatted = end_date_obj.strftime('%Y-%m-%d')
        #print(start_date_formatted)
        #print(end_date_formatted)
        return start_date_formatted, end_date_formatted
    else:
        return None, None  # Return a tuple of None to maintain consistency
        
  
  WD_PAGE_SIZE= 200       #set to max length of page in collection
def get_documents_from_wd(collection_ids=[os.environ["ELAWS_COLLECTION_ID"]]):
    logging.info("Fetching documents from Watson Discovery")
    documents = []
    logging.info("Configuring the WD client")
    authenticator = IAMAuthenticator(os.environ["WD_API_KEY"])
    wd_client = DiscoveryV2(
        version="2020-08-30",
        authenticator=authenticator
    )
    logging.info("Setting the WD service URL")
    wd_client.set_service_url(os.environ["WD_SERVICE_URL"])
    logging.info("Fetching documents from WD")
    page_id = 0
    retries = 0
    while True:
        try:
            logging.info("Fetching page: " + str(page_id))
            response = wd_client.query(
                project_id=os.environ["WD_PROJECT_ID"],
                collection_ids=collection_ids,
                #body text and date extraction from discovery
                return_=["text", "date", "extracted_metadata.filename", "metadata.source.SourceUrl"],           
                count=WD_PAGE_SIZE,
                offset=page_id*WD_PAGE_SIZE
            ).get_result()
            if response is None or not isinstance(response, dict):
                logging.info("No query result")
                raise ValueError("No query result")
            if "results" not in response or response["results"] is None or not isinstance(response["results"], list):
                logging.info("No query result 2")
                raise ValueError("No query result")
            results = response["results"]
            if len(results) == 0:
                logging.info("No more results")
                break
            logging.info("Fetched " + str(len(results)) + " documents")
            #Document class is text and metadata
            documents.extend(list(map(lambda result: Document(page_content=result["text"][0],  
                                                             metadata= {"start_date": extract_dates(str(result["date"]))[0],"end_date": extract_dates(str(result["date"]))[1],"collection_id": collection_ids, 
                                                                        "document_id" : result['document_id'], "url" : result['metadata']['source']['SourceUrl'], "filename": result['extracted_metadata']['filename']}), results)))
            page_id += 1
            
            # print(results[1]["metadata"]['source']['SourceUrl'])
            # print(results[1]['extracted_metadata']['filename'])
                
        except Exception as error:
            logging.error("Failed to fetch documents from WD", str(error))
            retries += 1
            time.sleep(5)
            if retries > MAX_RETRIES:
                break
            logging.info("Retrying...")
    logging.info("Fetched " + str(len(documents)) + " documents")
    
    return documents
def split_documents(documents, chunk_size, chunk_overlap):
    logging.info("Splitting documents")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap#
    )
    chunks = text_splitter.split_documents(documents)
    logging.info("Split into " + str(len(chunks)) + " chunks")
    return chunks   
    

chunks= split_documents(eLaws, chunk_size=500, chunk_overlap=100)

from langchain.embeddings import HuggingFaceInstructEmbeddings

embedding_function = HuggingFaceInstructEmbeddings(
            model_name="hkunlp/instructor-large",
            model_kwargs={"device": "cpu"},
            query_instruction="Represent the tax worker's query for retrieving supporting documents:",
            embed_instruction = "Represent the tax policy document for retrieval:"
)

from langchain_elasticsearch import ElasticsearchStore
from elasticsearch import Elasticsearch

es_client = Elasticsearch(
    url,
    basic_auth=(username,password),
    verify_certs=False,
    request_timeout=3600,
)
es_client.info()

db = ElasticsearchStore.from_documents(
    chunks,
    es_connection=es_client,
    embedding = embedding_function,
    index_name="elaws",
)
db.client.indices.refresh(index="elaws")

results = db.similarity_search(
    "employer installment", filter=[{"range": {"metadata.start_date": {"gte": "2007-07-08"}}}]
)
print(results)