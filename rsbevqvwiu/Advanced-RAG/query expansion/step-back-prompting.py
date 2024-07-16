from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModel
from pymilvus import Collection
import torch

# Step 1: Generate Intermediate Prompts
def generate_intermediate_prompts(query, model_name='t5-small', num_prompts=3):
    """
    Generates intermediate prompts to clarify or break down the original query.
    """
    # Initialize tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    # Generate intermediate prompts
    inputs = tokenizer.encode(f"clarify: {query}", return_tensors="pt")
    outputs = model.generate(inputs, max_length=50, num_return_sequences=num_prompts, num_beams=5)
    
    intermediate_prompts = [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
    return intermediate_prompts

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
def retrieve_documents(intermediate_prompts, collection, search_params, limit=10):
    """
    Retrieves documents from Milvus based on intermediate prompt embeddings.
    """
    all_documents = set()
    for prompt in intermediate_prompts:
        query_embedding = get_query_embedding(prompt)
        results = collection.search([query_embedding], "embedding", search_params, limit=limit, output_fields=["document"])
        documents = [hit.entity.get("document") for hit in results[0]]
        all_documents.update(documents)
    return list(all_documents)

# Step 4: Step Back Prompting RAG System
def step_back_prompting_rag(query, collection, model_name_t5='t5-small', model_name_embedding='sentence-transformers/all-MiniLM-L6-v2', num_prompts=3, search_params={"metric_type": "L2", "params": {"nprobe": 10}}, limit=10):
    """
    Performs a Retrieval-Augmented Generation (RAG) using step back prompting.
    """
    # Generate intermediate prompts
    intermediate_prompts = generate_intermediate_prompts(query, model_name=model_name_t5, num_prompts=num_prompts)
    
    # Retrieve documents from Milvus
    retrieved_documents = retrieve_documents(intermediate_prompts, collection, search_params, limit)
    
    return retrieved_documents

# Example usage
query = "machine learning applications"

# Assuming `collection` is your Milvus collection already set up and loaded
retrieved_docs = step_back_prompting_rag(query, collection)
print("Retrieved Documents:")
for doc in retrieved_docs:
    print(doc)
