from elasticsearch import Elasticsearch, helpers
import json
from dotenv import load_dotenv
import os


class ElasticsearchWrapper:
    def __init__(self, config_file="elastic_search.json"):
        load_dotenv()
        self.es_credentials = {
            "url": os.getenv("ELASTIC_URL",None),
            "username": os.getenv("ELASTIC_USERNAME",None),
            "use_anonymous_access": """false""",
            "password": os.getenv("ELASTIC_PASSWORD",None)
        }
        self.client = Elasticsearch(
            self.es_credentials["url"],
            basic_auth=(self.es_credentials["username"], self.es_credentials["password"]),
            verify_certs=False,
            request_timeout=3600
        )
        print("ES Client info:", self.client.info())
        config = {}
        with open(config_file) as config_fl:
            config = json.load(config_fl)

        self.model_type = config["MODEL_TYPE"]
        self.embedding_model_name = config["EMBEDDING_MODEL"]
        self.emb_dim = config["EMBEDDING_DIMENSION"]
        self.index_name = config["INDEX_NAME"]


    def ingest_bulk(self,index,documents):
        index_documents = [{"_index":index, "_source":source} for source in documents]
        helpers.bulk(self.client,index_documents)


    def search_by_keyword(self, index_name, keyword):
        query = {
            "query": {
                "match": {
                    "text": keyword
                }
            }
        }
        return self.client.search(index=index_name, body=query)


    def elser_search(self,index_name,query, model_name, lighthouse_id, top_k=5, min_score=3.7):
        return self.client.search(index=index_name, query={
            "bool": { 
                "must": [
                    {
                    "text_expansion": {
                        "ml.tokens": {
                        "model_text": query,
                        "model_id": model_name,
                        }
                     }
                    }],
                }
        },size=top_k, min_score=min_score)
    

    def get_simple_chunks(self, elastic_response):
        hits = elastic_response['hits']['hits']
        chunks = []
        scores = []

        for hit in hits:
            chunk = hit["_source"]["description"]
            score = hit["_score"]
            chunks.append(chunk)
            scores.append(score)

        return chunks, scores
    

    def hybrid_search(self, index_name, query_text, model_name, top_k=3):
        query = {
            "sub_searches": [
                {
                "query": {
                    "match": {
                    "description": query_text
                    }
                }
                },
                {
                "query": {
                    "text_expansion": {
                    "ml.tokens": {
                        "model_id": model_name,
                        "model_text": query_text
                    }
                    }
                }
                }
            ],
            "rank": {
                "rrf": {}
            }

        }
        return self.client.search(index=index_name, body=query)
    

if __name__ == "__main__":
    es = ElasticsearchWrapper()
    # ingestion
    documents = [] # add your docs here
    es.ingest_bulk(es.index_name, documents)

    # search
    input_query = "" # input your query here
    response = es.hybrid_search(es.index_name, input_query, es.embedding_model_name, top_k=3)
    chunks = es.get_simple_chunks(response)