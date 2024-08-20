from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyMuPDFLoader
from pymilvus import (
   FieldSchema, DataType,
   CollectionSchema, Collection, Milvus,connections,utility)
import os
from pymilvus import model


def read_chunk_data(file):
    loader_mu = PyMuPDFLoader(file)
    pages = loader_mu.load()
    text_splitter = RecursiveCharacterTextSplitter(
		chunk_size=800,
		chunk_overlap=60
	)
    docs_split = text_splitter.split_documents(pages)
    docs = [doc.page_content for doc in docs_split]
    return docs


def connects_to_milvus_db(file):
    MILVUS_HOST = str(os.environ.get("MILVUS_HOST"))
    MILVUS_PORT = str(os.environ.get("MILVUS_PORT"))
    MILVUS_PASSWORD = str(os.environ.get("MILVUS_PASSWORD"))
    client = connections.connect("default", host=MILVUS_HOST, 
										port=MILVUS_PORT, 
										secure=True, 
										server_pem_path="./cert.pem", 
										server_name="localhost",
										user="root",
										password=MILVUS_PASSWORD)
    splade_ef = model.sparse.SpladeEmbeddingFunction(model_name="naver/splade-cocondenser-selfdistil", 
                                                     device="cpu"
                                                    )
    collection_name = 'sparse_rag'
    if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
            print("Collection Dropped")
            
	# Create schema
    fields = [
		FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
		FieldSchema(name='sparse_vector', dtype=DataType.SPARSE_FLOAT_VECTOR, description='Sparse Embedding vectors') # Sparse Vector field 
		]
    schema = CollectionSchema(fields=fields,enable_dynamic_field=False)

	# Create collection
    collection = Collection(name=collection_name, schema=schema)
    
	#Define index params 
    sparse_index_params = {
    "index_name":"sparse_inverted_index",
    "index_type":"SPARSE_INVERTED_INDEX", # the type of index to be created. set to `SPARSE_INVERTED_INDEX` or `SPARSE_WAND`.
    "metric_type":"IP", # the metric type to be used for the index. Currently, only `IP` (Inner Product) is supported.
    "params":{"drop_ratio_build": 0.2}, # the ratio of small vector values to be dropped during indexing.
    }

	# Create index
    collection.create_index("sparse_vector", index_params=sparse_index_params)
    docs = read_chunk_data(file)
    docs_embeddings = splade_ef.encode_documents(docs)
    ids = [i for i in range(len(docs))]
    entities =[ids,docs_embeddings] 
    collection.insert(entities)
    query = "Type your query"
    query_vector = splade_ef.encode_queries(query)
    search_params = {
		"metric_type": "IP",
		"params": {"drop_ratio_search": 0.2}, # the ratio of small vector values to be dropped during search.
	}
    search_res = client.search(
		collection_name=collection_name,
		data=[query_vector],
		limit=3,
		output_fields=["id"],
		search_params=search_params,
	)
    for hits in search_res:
        for hit in hits:
               print(f"hit: {hit}")
    return search_res
        
                  

			

    
