import os
from typing import Optional, Dict
from elasticsearch import Elasticsearch
from elasticsearch_llm_cache.elasticsearch_llm_cache import ElasticsearchLLMCache

connection_details = {
    'username' :  os.environ["es_username"],
    'password' :  os.environ["es_password"],
    'url' : os.environ["es_url"],
    'cert_path': "ca.crt"
}

current_query = os.environ["current_query"]


class ElasticsearchLLMCacheHandler:
    def __init__(self, connection_details: Dict, index_name: Optional[str] = 'llm_cache_index'):
        self.connection_details = connection_details
        self.index_name = index_name
        self.es_client = self._create_es_client()
        self.llm_cache = self._initialize_llm_cache()

    def _create_es_client(self) -> Elasticsearch:
        try:
            es_client = Elasticsearch(
                self.connection_details["url"],
                basic_auth = (self.connection_details["username"], self.connection_details["password"]),
                verify_certs =  False,
                # ca_certs = self.connection_details['cert_path'],
                request_timeout = 3600
            )
            if not es_client.ping():
                raise ValueError("Connection failed")
            print("Elasticsearch client created successfully")
            return es_client
        except Exception as e:
            print(f"Error creating Elasticsearch client: {e}")
            raise

    def _initialize_llm_cache(self) -> ElasticsearchLLMCache:
        try:
            llm_cache = ElasticsearchLLMCache(
                es_client = self.es_client, 
                index_name = self.index_name, 
                es_model_id = ".multilingual-e5-small_linux-x86_64", 
                create_index = False
            )
            if not self._index_exists():
                llm_cache.create_index(dims = 384)
                print("Index created")
            else:
                print("Index already exists")
            return llm_cache
        except Exception as e:
            print(f"Error initializing ElasticsearchLLMCache: {e}")
            raise

    def _index_exists(self) -> bool:
        try:
            return self.es_client.indices.exists(index = self.index_name)
        except Exception as e:
            print(f"Error checking if index exists: {e}")
            raise

    def query_cache(self, current_query: str, similarity_threshold: Optional[float] = 0.9, num_candidates: int = 1) -> Dict:
        try:
            response = self.llm_cache.query(prompt_text = current_query, similarity_threshold = similarity_threshold, num_candidates = num_candidates)
            print(f"Cache query successful: {response}")
            return response
        except Exception as e:
            print(f"Error querying cache: {e}")
            return {}

    def add_to_cache(self, current_query: str, llm_response: str, source: Optional[str] = None) -> Dict:
        try:
            result = self.llm_cache.add(prompt = current_query, response = llm_response, source = source)
            print(f"Added to cache: {result}")
            return result
        except Exception as e:
            print(f"Error adding to cache: {e}")
            return {}
            
            
try:
    cache_handler = ElasticsearchLLMCacheHandler(connection_details = connection_details, index_name = "llm_cache_test_v1")
    
    # Query the cache
    cache_response = cache_handler.query_cache(current_query = current_query)
    
    # If no cache hit, add new response to cache
    if not cache_response:
        llm_response = "I'm here to assist you!"  # Assume this response is fetched from LLM
        cache_handler.add_to_cache(current_query = current_query, llm_response = llm_response)
    else:
      print(current_query)
      print(cache_response)

except Exception as e:
    print(f"An error occurred: {e}")