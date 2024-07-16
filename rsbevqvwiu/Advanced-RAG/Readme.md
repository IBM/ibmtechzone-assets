## Retrieval-Augmented Generation (RAG) Techniques using Milvus

This repository demonstrates various techniques for Retrieval-Augmented Generation (RAG) using Milvus for efficient document retrieval based on query expansions. The following techniques are implemented:

1. Cross-Encoder Reranking
2. Multi Query Expansion
3. Step Back Prompting
4. Hypothetical Answer Expansion

These techniques leverage transformer models for query expansion and Milvus for fast and scalable document retrieval based on embeddings.

## Dependencies

Ensure you have the following dependencies installed:

transformers==4.11.3
torch==1.10.0
pymilvus==2.0.0
sentence-transformers==2.1.0
