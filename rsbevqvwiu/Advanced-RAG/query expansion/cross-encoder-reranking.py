from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def cross_encoder_reranking(queries, collection, model_name='cross-encoder/ms-marco-TinyBERT-L-2'):
    # Initialize tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    reranked_results = []
    for query in queries:
        query_embedding = get_query_embedding(query)  # Define this function based on your setup
        
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search([query_embedding], "embedding", search_params, limit=10, output_fields=["document"])
        
        documents = [hit.entity.get("document") for hit in results[0]]
        
        scores = []
        for doc in documents:
            inputs = tokenizer.encode_plus(query, doc, return_tensors='pt')
            with torch.no_grad():
                outputs = model(**inputs)
            scores.append((doc, outputs.logits.item()))
        
        reranked_results.append(sorted(scores, key=lambda x: x[1], reverse=True))
    
    return reranked_results

def get_query_embedding(query, model_name='sentence-transformers/all-MiniLM-L6-v2'):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    inputs = tokenizer(query, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

# Example usage
queries = ["What is machine learning?", "Best practices for deep learning"]

results = cross_encoder_reranking(queries, collection)
for query, reranked in zip(queries, results):
    print(f"Query: {query}")
    for rank, (doc, score) in enumerate(reranked, 1):
        print(f"{rank}: {doc} (Score: {score:.4f})")
    print()
