from __future__ import annotations
from langchain.schema.document import Document
from langchain.retrievers import BM25Retriever
from typing import Dict, Optional, Sequence
from langchain.schema import Document
from langchain.pydantic_v1 import Extra
from langchain.callbacks.manager import Callbacks
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
from sentence_transformers import CrossEncoder
from langchain.retrievers import ContextualCompressionRetriever


#Using simple BM25 retriever. Please replace it with suitable retriever like elasticsearch or weaviate or faiss
retriever = BM25Retriever.from_documents(
    [
        Document(page_content="Open: Based on open technologies that provide a variety of models to cover enterprise use cases and compliance requirements."),
        Document(page_content="Targeted: Targeted to specific enterprise domains like HR, customer service or IT operations to unlock new value. "),
        Document(page_content="Trusted: Designed with principles of transparency, responsibility and governance so you can manage legal, regulatory, ethical and accuracy concerns."),
        Document(page_content="Empowering: Go beyond being an AI user and become an AI value creator, owning the value your models create."),
        Document(page_content="Deploy assistants to automate workflows and implement AI across a variety of business and technical functions such as customer service, HR and code development. "),
    ]
)

class BgeRerank(BaseDocumentCompressor):
    model_name:str = 'BAAI/bge-reranker-large'  
    """Model name to use for reranking."""    
    top_n: int = 10   
    """Number of documents to return."""
    model:CrossEncoder = CrossEncoder(model_name)
    """CrossEncoder instance to use for reranking."""

    def bge_rerank(self,query,docs):
        model_inputs =  [[query, doc] for doc in docs]
        scores = self.model.predict(model_inputs)
        results = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return results[:self.top_n]


    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """
        Compress documents using BAAI/bge-reranker models.

        Args:
            documents: A sequence of documents to compress.
            query: The query to use for compressing the documents.
            callbacks: Callbacks to run during the compression process.

        Returns:
            A sequence of compressed documents.
        """
        if len(documents) == 0:  # to avoid empty api call
            return []
        doc_list = list(documents)
        _docs = [d.page_content for d in doc_list]
        results = self.bge_rerank(query, _docs)
        final_results = []
        for r in results:
            doc = doc_list[r[0]]
            doc.metadata["relevance_score"] = r[1]
            final_results.append(doc)
        return final_results
    
compressor = BgeRerank(top_n=3)
compression_retriever_bge = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)

query = "Are watsonx LLMs reliable?"
#Example usage 1
compressed_docs = compression_retriever_bge.get_relevant_documents(query=query)

print('Method 1:')
for compressed_doc in compressed_docs:
    print(compressed_doc.page_content)

#Example usage 2

bm25_docs = retriever.invoke(query)
bge_docs = compressor.compress_documents(bm25_docs,query)

print('Method 2')
print('Before reranking')
for bm25_doc in bm25_docs:
    print(bm25_doc.page_content)

print('After reranking')
for compressed_doc in bge_docs:
    print(compressed_doc.page_content)