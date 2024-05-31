### CHROMA DB - RAG

# IMPORTING NECESSARY LIBRARIES 
import os
import numpy as np
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter
from sentence_transformers import CrossEncoder
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams 
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from pypdf import PdfReader

def get_wml_creds():
    load_dotenv()
    api_key = os.getenv("API_KEY", None)
    ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
    project_id = os.getenv("PROJECT_ID", None)
    if api_key is None or ibm_cloud_url is None or project_id is None:
        print("Ensure you copied the .env file that you created earlier into the same directory as this notebook")
    else:
        creds = {
            "url": ibm_cloud_url,
            "apikey": api_key 
        }
    return project_id, creds


project_id, creds = get_wml_creds()


def word_wrap(string, n_chars=72):
    if len(string) < n_chars:
        return string
    else:
        return string[:n_chars].rsplit(' ', 1)[0] + '\n' + word_wrap(string[len(string[:n_chars].rsplit(' ', 1)[0])+1:], n_chars)


reader = PdfReader("YOUR-PDF-PATH.pdf")
pdf_texts = [p.extract_text().strip() for p in reader.pages]

# Filter the empty strings
pdf_texts = [text for text in pdf_texts if text]

character_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=1000,
    chunk_overlap=0
)
character_split_texts = character_splitter.split_text('\n\n'.join(pdf_texts))

token_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0, tokens_per_chunk=256)

token_split_texts = []
for text in character_split_texts:
    token_split_texts += token_splitter.split_text(text)


embedding_function = SentenceTransformerEmbeddingFunction()
print(embedding_function([token_split_texts[10]]))

# chroma_client.delete_collection(name="COLLECTION_NAME")  
#RUN this if collection already exists 

## creating a collection with name COLLECTION_NAME

chroma_client = chromadb.Client()
chroma_collection = chroma_client.create_collection("COLLECTIOIN_NAME", embedding_function=embedding_function)
ids = [str(i) for i in range(len(token_split_texts))]

chroma_collection.add(ids=ids, documents=token_split_texts)
chroma_collection.count()


chroma_client.list_collections()

### SELECT YOUR LLM MODEL

def send_to_watsonxai(prompt, model_id="ibm/granite-13b-chat-v2"):     
    params = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MIN_NEW_TOKENS: 1,
        GenParams.MAX_NEW_TOKENS: 200,
        GenParams.TEMPERATURE: 0,
    }

    model = Model(model_id='ibm/granite-13b-chat-v2', params=params, credentials=creds, project_id=project_id)
    response = model.generate_text(prompt)
    return response


def make_prompt(context, question_text):
    return (f"{context}\n\nPlease answer a question using this "
          + f"text. "
          + f"If the question is unanswerable, say \"unanswerable\"."
          + f"Question: {question_text}")


cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

### RAG FUNCTION

def nordea_qa(query):
    results = chroma_collection.query(query_texts=[query], n_results=10, include=['documents', 'embeddings'])
    retrieved_documents = results['documents'][0]

    pairs = [[query, doc] for doc in retrieved_documents]
    scores = cross_encoder.predict(pairs)

    ordered_retrieve_documents = list()
    for o in np.argsort(scores)[::-1]:
        ordered_retrieve_documents.append(retrieved_documents[o])

    context = "\n\n\n".join(ordered_retrieve_documents[:4])
    prompt = make_prompt(context, query)
    response = send_to_watsonxai(prompt)

    return response, context

### Extraction

query = "What is this document about?"

answer_scope, context = nordea_qa(query)

print("Question = ", query)
print("Answer = ", answer_scope)
print("\n\nContext =\n", context)


