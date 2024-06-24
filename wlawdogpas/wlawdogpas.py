from elasticsearch import AsyncElasticsearch
from elasticsearch import Elasticsearch, AsyncElasticsearch
from langchain.text_splitter import CharacterTextSplitter
from elasticsearch.helpers import scan, bulk
import pandas as pd
from langchain.vectorstores.elasticsearch import ElasticsearchStore
import copy
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from dotenv import load_dotenv
dest_index_name='test1-index2'

client=AsyncElasticsearch(hosts=elasticsearch_url, basic_auth=(username, password),verify_certs=False)
if es_connection.indices.exists(index=dest_index_name):
    es_connection.indices.delete(index=dest_index_name)

prmpt="""
[INST]<<SYS>>You are a helpful, respectful, and honest assistant. Always answer as helpfully as possible, while being safe. Be brief in your answers. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don\\'\''t know the answer to a question, please do not share false information. <</SYS>>
\nGenerate the next agent response by answering the question. You are provided several documents with titles. If the answer comes from different documents please mention all possibilities and use the tiles of documents to separate between topics or domains. Answer with no more than 150 words. If you cannot base your answer on the given document, please state that you do not have an answer.
\nPlease dont mention about the context or Source document in your response.
\nContext:{context}
{chat_history}<</SYS>>\n\n
{question} Answer with no more than 150 words. If you cannot base your answer on the given document, please state that you do not have an answer. [/INST]

response:
"""
wx_credentials = {
    "url": wx_url,
    "apikey": wx_api
}

parameters = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
    GenParams.MAX_NEW_TOKENS: 300,
    GenParams.MIN_NEW_TOKENS: 5,
    GenParams.TEMPERATURE: 0.2,
    "repetition_penalty": 1.3,
    "hap": {
      "threshold": 0.75,
      "input": True,
      "output": True
    },
    "stigma": {
      "threshold": 0.75,
      "input": True,
      "output": True
    }
}

wx_model = Model(
    model_id=ModelTypes.LLAMA_2_70B_CHAT,
    params=parameters,
    credentials=wx_credentials,
    project_id=wx_project_id
)

watsonx_llm = WatsonxLLM(model=wx_model)
from llama_index.vector_stores import ElasticsearchStore
from llama_index import StorageContext
from llama_index import ServiceContext
from llama_index.embeddings import ElasticsearchEmbedding
from llama_index.embeddings import HuggingFaceEmbedding
vector=ElasticsearchStore(es_client=client, index_name=dest_index_name)
from llama_index import SimpleDirectoryReader, VectorStoreIndex
docs=SimpleDirectoryReader('/Users/vishwajithcr/Documents/workdocs/Projects/DEFRA_EA_Digital_AVATAR/EA ICS and NCCC Existing Knowledge base and Call Outcomes/docs',recursive=True,exclude=['.xlsx'])
raw_documents = docs.load_data()
embed_model = HuggingFaceEmbedding(model_name='sentence-transformers/all-MiniLM-L12-v2')
storage_context = StorageContext.from_defaults(vector_store=vector)
embed=ElasticsearchEmbedding.from_es_connection(es_connection=es_connection, model_id='.elser_model_1')
index = VectorStoreIndex.from_documents(
    raw_documents,
    storage_context=storage_context,
    service_context=ServiceContext.from_defaults(llm=watsonx_llm, embed_model=embed,
                                                           system_prompt=prmpt, chunk_size=400, chunk_overlap=50)
)
