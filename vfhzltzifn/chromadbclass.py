import chromadb
import uuid
from chromadb.api.types import EmbeddingFunction
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import re
import warnings
warnings.filterwarnings("ignore")

class ChromaDBHandler:
    def __init__(self, collection_name='trial_criteria'):
        """Initialize the ChromaDBHandler with a collection name and embedding function."""
        self.collection_name = collection_name
        self.client = chromadb.Client()
        self.emb_function = MiniLML6V2EmbeddingFunction()

        self.vstore = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.emb_function,
            metadata={"hnsw:space": "cosine"}
        )

    def delete_all_data(self):
        """Delete all data inside the collection without deleting the collection itself."""
        if self.vstore.count() > 0:
            self.vstore.delete(ids=self.vstore.get()['ids'])
            print(f"All data deleted from the collection: {self.collection_name}")
        else:
            print(f"No data to delete in the collection: {self.collection_name}")

    def insert_data(self, criteria):
        """Insert data into the collection by splitting it into chunks."""
        
        chunks = [chunk.strip() for chunk in criteria.split('*') if chunk.strip()]

        
        # print(f"Inserting criteria into ChromaDB: {chunks}")

        for i, chunk in enumerate(chunks):
            
            
            if chunk not in ['\\', '\\\\'] and not chunk.lower().startswith(('inclusion criteria', 'exclusion criteria')):
                self.vstore.add(
                    documents=[chunk],
                    metadatas=[{'chunk_number': i + 1}],
                    ids=[str(uuid.uuid1())]
                )

    def query_data(self, query_text, n_results=3):
        """Query the collection and return the top matching documents."""
        query_text = re.sub(r'\s+', ' ', query_text).strip()
        query_embedding = self.emb_function([query_text])
        results = self.vstore.query(query_embeddings=query_embedding, n_results=n_results)

        
        if 'documents' in results and len(results['documents']) > 0:
            
            valid_results = [doc for doc in results['documents'][0] if doc and doc not in ['\\', '\\\\'] and not doc.lower().startswith(('inclusion criteria', 'exclusion criteria'))]
            if valid_results:
                # print(f"Querying for: '{query_text}' yielded results: {valid_results}")
                return " ".join(valid_results)
            else:
                # print(f"Querying for: '{query_text}' yielded no valid results.")
                return "No matching reference found"
        else:
            # print(f"Querying for: '{query_text}' yielded no results.")
            return "No matching reference found"


class MiniLML6V2EmbeddingFunction(EmbeddingFunction):
    """Embedding function using the all-MiniLM-L12-v2 model."""
    MODEL = SentenceTransformer('all-MiniLM-L6-v2')

    def __call__(self, texts):
        return MiniLML6V2EmbeddingFunction.MODEL.encode(texts).tolist()