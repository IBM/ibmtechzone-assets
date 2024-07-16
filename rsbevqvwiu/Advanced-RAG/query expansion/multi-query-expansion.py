from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModel
from pymilvus import Collection
import torch

# Step 1: Multi Query Expansion
def multi_query_expansion(query, model_name='t5-small', num_queries=5):
    """
    Expands a given query into multiple variations using a T5 model.
    """
    # Initialize tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    # Generate multiple query variations
    inputs = tokenizer.encode(f"expand: {query}", return_tensors="pt")
    outputs = model.generate(inputs, max_length=50, num_return_sequences=num_queries, num_beams=5)
    
    expanded_queries = [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
    return expanded_queries

# Step 2: Query Embedding
def get_query_embedding(query, model_name='sentence-transformers/all-MiniLM-L6-v2'):
    """
    Converts a query into an embedding using a Sentence Transformer model.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    inputs = tokenizer(query, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

# Step 3: Retrieve Documents from Milvus
def retrieve_documents(expanded_queries, collection, search_params, limit=10):
    """
    Retrieves documents from Milvus based on expanded query embeddings.
    """
    all_documents = set()
    for query in expanded_queries:
        query_embedding = get_query_embedding(query)
        results = collection.search([query_embedding], "embedding", search_params, limit=limit, output_fields=["document"])
        documents = [hit.entity.get("document") for hit in results[0]]
        all_documents.update(documents)
    return list(all_documents)

# Step 4: Multi Query RAG System
def multi_query_rag(query, collection, model_name_t5='t5-small', model_name_embedding='sentence-transformers/all-MiniLM-L6-v2', num_queries=5, search_params={"metric_type": "L2", "params": {"nprobe": 10}}, limit=10):
    """
    Performs a Retrieval-Augmented Generation (RAG) using multi query expansion.
    """
    # Generate expanded queries
    expanded_queries = multi_query_expansion(query, model_name=model_name_t5, num_queries=num_queries)
    
    # Retrieve documents from Milvus
    retrieved_documents = retrieve_documents(expanded_queries, collection, search_params, limit)
    
    return retrieved_documents

# Example usage
query = "machine learning applications"

# Assuming `collection` is your Milvus collection already set up and loaded
retrieved_docs = multi_query_rag(query, collection)
print("Retrieved Documents:")
for doc in retrieved_docs:
    print(doc)
