from typing import Any, List, Optional
from langchain.schema import Document
from transformers import AutoTokenizer, AutoModel
import torch

class ColbertReranker:
    def __init__(self, tokenizer="colbert-ir/colbertv2.0", model="colbert-ir/colbertv2.0"):
        self._tokenizer = AutoTokenizer.from_pretrained(tokenizer)
        self._model = AutoModel.from_pretrained(model)

    def calculate_sim(self, query: str, documents_text_list: List[str]):
        query_encoding = self._tokenizer(query, return_tensors="pt")
        query_embedding = self._model(**query_encoding).last_hidden_state
        rerank_score_list = []

        for document_text in documents_text_list:
            document_encoding = self._tokenizer(
                document_text, return_tensors="pt", truncation=True, max_length=512
            )
            document_embedding = self._model(**document_encoding).last_hidden_state

            sim_matrix = torch.nn.functional.cosine_similarity(
                query_embedding.unsqueeze(2), document_embedding.unsqueeze(1), dim=-1
            )

            # Take the maximum similarity for each query token (across all document tokens)
            # sim_matrix shape: [batch_size, query_length, doc_length]
            max_sim_scores, _ = torch.max(sim_matrix, dim=2)
            rerank_score_list.append(torch.mean(max_sim_scores, dim=1).item())

        return rerank_score_list
    
    def rerank(self, query: str, docs: Document):
        documents_text_list = [doc.page_content for doc in docs]
        scores = self.calculate_sim(query=query, documents_text_list=documents_text_list)
        docs_with_score = tuple(zip(docs, scores))
        reranked_docs = sorted(docs_with_score, key=lambda x: x[1], reverse=True)
        return reranked_docs