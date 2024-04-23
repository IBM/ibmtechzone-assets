from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
import os
load_dotenv()

es_url = os.getenv("ES_URL")
es_user = os.getenv("ES_USER")
es_password = os.getenv("ES_PASSWORD")
es_index = os.getenv("ES_INDEX")
es_cert = os.getenv("ES_CERT")

class ContextRetriever:
    def __init__(self, parent_doc_path, embedding_modelname = "intfloat/multilingual-e5-large", parent_chunk_size=2000, child_chunk_size=400) -> None:
        self._elasticsearch_store = self.__get_elasticsearch_store(
            es_url, es_user, es_password, 
            es_index, es_cert, embedding_modelname
        )
        self._docstore = self.__get_parent_docstore(parent_doc_path)
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=100, separators=["\n\n", " "])
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=child_chunk_size, chunk_overlap=40, separators=["\n\n", " "])
        self._retriever = ParentDocumentRetriever(
            vectorstore=self._elasticsearch_store,
            docstore=self._docstore,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
        )

    def __get_elasticsearch_store(self, es_url, es_user, es_password, es_index, es_cert, embedding_modelname):
        model_kwargs = {'device': 'cpu'}
        embeddings_model = HuggingFaceEmbeddings(
            model_name=embedding_modelname,
            model_kwargs=model_kwargs
        )
        es = Elasticsearch(
            [es_url],
            basic_auth=(es_user, es_password),
            ca_certs=es_cert,
            verify_certs=True
        )
        # The vectorstore to use to index the child chunks
        elastic_vector_search = ElasticsearchStore(
            es_connection=es,
            index_name=es_index,
            embedding=embeddings_model
        )
        return elastic_vector_search

    def __get_parent_docstore(self, parent_doc_path):
        fs = LocalFileStore(parent_doc_path)
        store = create_kv_docstore(fs)
        return store
    
    def add_documents(self, docs):
        self._retriever.add_documents(docs)
    
    def get_relevant_docs(self, query, file_name="", num_chunks=4):
        if file_name != "":
            self._retriever.search_kwargs = {"k": num_chunks, "filter":[{"term": {"metadata.file_name.keyword": file_name}}]}
        else:
            self._retriever.search_kwargs = {"k": num_chunks}
        relevant_docs = self._retriever.get_relevant_documents(query)
        return relevant_docs
    
    def get_relevant_docs_with_similarity(self, query, file_name="", num_chunks=4):
        if file_name != "":
            search_kwargs = {"k": num_chunks, "filter":[{"term": {"metadata.file_name.keyword": file_name}}]}
        else:
            search_kwargs = {"k": num_chunks}
        sub_docs = self._elasticsearch_store.similarity_search_with_score(query, **search_kwargs)
        ids = []
        scores = []
        for d, score in sub_docs:
            if "doc_id" in d.metadata and d.metadata["doc_id"] not in ids:
                ids.append(d.metadata["doc_id"])
                scores.append(score)
        docs = self._docstore.mget(ids)
        docs_score = list(zip(ids, docs, scores))
        return [d for d in docs_score if d is not None]