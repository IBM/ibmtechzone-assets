from typing import Any, List, Optional
from langchain.schema import Document
from sentence_transformers import CrossEncoder

class CrossEncoderReranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        self._cross_encoder = CrossEncoder(model_name)

    def calculate_sim(self, query: str, documents_text_list: List[str]):
        pairs = [[query, doc] for doc in documents_text_list]
        scores = self._cross_encoder.predict(pairs)
        return scores
    
    def rerank(self, query: str, docs: Document):
        documents_text_list = [doc.page_content for doc in docs]
        scores = self.calculate_sim(query=query, documents_text_list=documents_text_list)
        docs_with_score = tuple(zip(docs, scores))
        reranked_docs = sorted(docs_with_score, key=lambda x: x[1], reverse=True)
        return reranked_docs