from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
from langchain_core.documents import Document
from elasticsearch import Elasticsearch

from typing import Dict
import torch
import pandas as pd
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models import Model


from unstructured.staging.base import elements_to_json
from unstructured.partition.pdf import partition_pdf
import os


from pdfminer.high_level import extract_text
from ragatouille import RAGPretrainedModel

RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

from langchain.retrievers import ContextualCompressionRetriever

instructor_embeddings: HuggingFaceEmbeddings = None
def load_transformer():
    global instructor_embeddings
    instructor_embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-large")
load_transformer()

def read_pdf(file_path):
    documents = extract_text(file_path)
    return documents

def create_chunks(documents, file_path):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2048,
        chunk_overlap=200
    )
    chunks = text_splitter.split_text(documents)
    texts = [
        Document(page_content=chunk, metadata={'source': file_path, 'page': i})
        for i, chunk in enumerate(chunks)
    ]
    return texts

def save_embeddings(collection_name, texts):
    es_connection = Elasticsearch(
            "elastic_url",
            basic_auth=("elastic_user", "elastic_password"),
            verify_certs=False,
            ssl_show_warn=False)

    vectordb = ElasticsearchStore.from_documents(
        documents=texts,
        embedding=instructor_embeddings,
        index_name=f"index_{collection_name.replace('-', '_')}",
        es_connection=es_connection,
        strategy=ElasticsearchStore.ApproxRetrievalStrategy(hybrid=True, rrf=False),
        distance_strategy="COSINE",
        timeout=900)
    return vectordb

def create_retriever(vectordb, k):
    retriever = vectordb.as_retriever(search_kwargs={"k": k})
    return retriever

RAG_PROMPT = '''<INSTURCTION>
Act as a question and answer system. Only use the following pieces of context to answer the question at the end. If you can't find the answer from the given context, just say that you don't know, please don't try to make up an answer.
Return the response in the below format only, do not add or generate any extra information,

Answer: Aswer to the given question. Should not be a one word answer. If it can be answered in one word, place make a sentence out of it based on the question.
Page Number: page number under which the answer is found in the given context.

Leave it blank or simple say I don't know, if you didn't find Answer or Page Number.
</INSTRUCTION>

<CONTEXT>
{documents_context} 

</CONTEXT>
<QUESTION>
{question}
</QUESTION>

<ANSWER>

'''

def get_credentials():
    return {
        "url" : "cloud_url",
        "apikey" : "apikey",
        "project_id" : "project_id"
        }  
def watsonx_model(model_name, decoding_method, max_new_tokens, min_new_tokens, random_seed, temperature, stop_sequences, repetition_penalty):
    creds = get_credentials()

    model_params = {
        GenParams.DECODING_METHOD: decoding_method,
        GenParams.MIN_NEW_TOKENS: min_new_tokens,
        GenParams.MAX_NEW_TOKENS: max_new_tokens,
        GenParams.RANDOM_SEED: random_seed,
        GenParams.TEMPERATURE: temperature,
        GenParams.STOP_SEQUENCES: stop_sequences,
        GenParams.REPETITION_PENALTY: repetition_penalty
    }
    model = Model(model_id=model_name, params=model_params, credentials=creds, project_id=creds["project_id"])
    return model

def reranker_colbert(entity, retriever):
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=RAG.as_langchain_document_compressor(), base_retriever=retriever
    )
    reranked_colbert = compression_retriever.invoke(
        entity
    )
    return reranked_colbert

def extract_metadata(file_path):
        include_page_breaks = True
        strategy = "hi_res"
        if strategy == "hi_res": infer_table_structure = True
        else: infer_table_structure = False
        if infer_table_structure == True: extract_element_types=[ "Header","Footer"]
        else: extract_element_types=None
        if strategy != "ocr_only": max_characters = None
        languages = ["eng"] 
        hi_res_model_name = "yolox"

        elements = partition_pdf(
                filename=file_path,
                include_page_breaks=include_page_breaks,
                strategy=strategy,
                infer_table_structure=infer_table_structure,
                extract_element_types=extract_element_types,
                max_characters=max_characters,
                languages=languages,
                hi_res_model_name=hi_res_model_name,
                )

        elements_to_json(elements, filename=file_path.split("/")[-1].replace(".pdf","")+"metadata.json")
        df1=pd.read_json(file_path.split("/")[-1].replace(".pdf","")+"metadata.json")
        header_elements = list(df1.loc[(df1['type']=='Header'), "text"].unique())
        footer_elements = list(df1.loc[(df1['type']=='Footer'), "text"].unique())
        os.remove(file_path.split("/")[-1].replace(".pdf","")+"metadata.json")
        return header_elements, footer_elements

def clean_chunk(text, header_elements, footer_elements):
    content = text.split("\n")
    content = [line.strip() for line in content if line.strip()]
    content = [element for element in content if element not in header_elements]
    content = [element for element in content if element not in footer_elements]

file_path = "Santander.pdf"
collection_name = "Santander_collection"

print("Reading document..")
documents = read_pdf(file_path)
print("Create chunks..")
texts = create_chunks(documents, file_path)
print("Saving embeddings..")
vectordb = save_embeddings(collection_name, texts)
print("Creating retriever..")
retriever = create_retriever(vectordb, 10)
qa_model = watsonx_model(model_name='meta-llama/llama-3-70b-instruct', decoding_method="greedy", max_new_tokens=500, 
                         min_new_tokens=1, temperature=0.0, random_seed = 42,stop_sequences=None,repetition_penalty=1.05
                        )
query = "What are the ISIN codes mentioned in the broucher?"
docs = retriever.get_relevant_documents(query)
reranked_colbert = reranker_colbert(query, retriever)
reranked_docs = pd.DataFrame([(query, doc.page_content, doc.metadata) for doc in reranked_colbert], columns=['query', 'paragraph','metadata']) 
reranked_docs
header_elements, footer_elements = extract_metadata(file_path)
reranked_docs['page_content'] = reranked_docs['page_content'].apply(clean_chunk)
reranked_docs['page_content'] = reranked_docs['page_content'].apply(lambda x: clean_chunk(x, header_elements, footer_elements))
