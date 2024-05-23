# %%
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# %%
import chromadb

# %%
from pypdf import PdfReader

reader = PdfReader("2022_Annual_Report.pdf")
pdf_texts = [p.extract_text().strip() for p in reader.pages]

# Filter the empty strings
pdf_texts = [text for text in pdf_texts if text]

print(pdf_texts[0])

# %%
from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter

# %%
character_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=1000,
    chunk_overlap=0
)
character_split_texts = character_splitter.split_text('\n\n'.join(pdf_texts))

print(character_split_texts[10])
print(f"\nTotal chunks: {len(character_split_texts)}")

# %%
token_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0, tokens_per_chunk=256)

token_split_texts = []
for text in character_split_texts:
    token_split_texts += token_splitter.split_text(text)

# print(word_wrap(token_split_texts[10]))
print(f"\nTotal chunks: {len(token_split_texts)}")

# %%
token_split_texts[0]

# %%
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

embedding_function = SentenceTransformerEmbeddingFunction()
print(embedding_function([token_split_texts[10]]))

# %%
chroma_client = chromadb.Client()
chroma_collection = chroma_client.create_collection("2022_Annual_Report.pdf", embedding_function=embedding_function)

ids = [str(i) for i in range(len(token_split_texts))]

chroma_collection.add(ids=ids, documents=token_split_texts)
chroma_collection.count()

# %%
len(token_split_texts)

# %%
type(chroma_collection)

# %%
from dotenv import load_dotenv
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.foundation_models import Model
import pandas as pd
import os

# %%
params = {
    GenParams.DECODING_METHOD: "sample",
    GenParams.MAX_NEW_TOKENS: 800,
    GenParams.MIN_NEW_TOKENS: 50,
    GenParams.TOP_K: 5,
    GenParams.TOP_P: 0.6,
    GenParams.TEMPERATURE: 0.1
}

# %%
load_dotenv()
url = os.getenv("IBM_CLOUD_URL", None)
apikey = os.getenv("IBM_CLOUD_API_KEY", None)
project_id = os.getenv("PROJECT_ID", None)

WATSONX_APIKEY = os.getenv("IBM_CLOUD_API_KEY", None)
creds = {
    "url": url,
    "apikey": apikey
}

# %%
import requests

def get_bearer_token(wx_api_key):
        token_url = "https://iam.cloud.ibm.com/identity/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = {
            "apikey": wx_api_key,
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        }
        response = requests.post(token_url, headers=headers, data=data)
        token = response.json()["access_token"]
        return token

# %%
be_to = get_bearer_token(WATSONX_APIKEY)
print(be_to)

# %%
def generate_answer(model, instruction, question, token):
        # logs = Logs()
        # logs.log_event("generate_answer")
        # Preparing context for model inputs
        # context = search_result_gen["content"].str.cat(sep='\n')
        input_txt = question
        # Using the stored instruction for the prompt
        prompt = instruction
        # Model calling and response processing
        url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token
        }
        data = {
            "model_id": model,
            "project_id": project_id,
            "input": prompt + '\n\n' + "Input: " + input_txt + "\n\n" + "Output: ",
            "parameters": {
                "decoding_method": "greedy",
                "min_new_tokens": 1,
                "max_new_tokens": 500,
                "beam_width": 1
            }
        }
        response = requests.post(url, headers=headers, json=data)
        response = response.json()["results"][0]["generated_text"]
        
        return response

# %%
model = "meta-llama/llama-2-70b-chat"
instruction = "You are a helpful expert financial research assistant. Provide an example answer to the given question, that might be found in a document like an annual report."
question = "Was there significant turnover in the executive team?"
answer = generate_answer(model, instruction, question, be_to)

# %%
print(answer)

# %%
# original_query = "Was there significant turnover in the executive team?"
# hypothetical_answer = send_to_watsonxai(original_query)

joint_query = f"{question} {answer}"
print(joint_query)

# %%
results = chroma_collection.query(query_texts=joint_query, n_results=5, include=['documents', 'embeddings'])
retrieved_documents = results['documents'][0]

for doc in retrieved_documents:
    print(doc)
    print('')

# %%
list(results.keys())

# %%
results['documents'][0]

# %%
query = "What was the total revenue?"

results = chroma_collection.query(query_texts=[query], n_results=5)
retrieved_documents = results['documents'][0]

for document in retrieved_documents:
    print(document)
    print('\n')

# %%
import requests

def get_bearer_token(wx_api_key):
    token_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {
        "apikey": wx_api_key,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    }
    response = requests.post(token_url, headers=headers, data=data)
    token = response.json()["access_token"]
    return token

def generate_answer(model, instruction, query, information, token):
    # Prepare context for model inputs
    prompt = instruction
    input_txt = f"Question: {query}. Information: {information}"
    
    # Model calling and response processing
    url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    data = {
        "model_id": model,
        "project_id": project_id,
        "input": prompt + '\n\n' + "Input: " + input_txt + "\n\n" + "Output: ",
        "parameters": {
            "decoding_method": "greedy",
            "min_new_tokens": 1,
            "max_new_tokens": 500,
            "beam_width": 1
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response = response.json()["results"][0]["generated_text"]
    
    return response

# Retrieve documents
query = "What was the total revenue?"
results = chroma_collection.query(query_texts=[query], n_results=5)
retrieved_documents = results['documents'][0]

# Get IBM Watson API token
wx_api_key = WATSONX_APIKEY
wx_api_token = get_bearer_token(wx_api_key)

# Define model and instruction
model = "meta-llama/llama-2-70b-chat"
instruction = "You are a helpful expert financial research assistant. Your users are asking questions about information contained in an annual report. You will be shown the user's question, and the relevant information from the annual report. Answer the user's question using only this information."

# Generate answer
output = generate_answer(model, instruction, query, "\n\n".join(retrieved_documents), wx_api_token)

print(output)


# %%
# pip install umap

# %%
# pip install umap-learn

# %%
import umap
import numpy as np
from tqdm import tqdm

embeddings = chroma_collection.get(include=['embeddings'])['embeddings']
umap_transform = umap.UMAP(random_state=0, transform_seed=0).fit(embeddings)

# %%
def project_embeddings(embeddings, umap_transform):
    umap_embeddings = np.empty((len(embeddings),2))
    for i, embedding in enumerate(tqdm(embeddings)): 
        umap_embeddings[i] = umap_transform.transform([embedding])
    return umap_embeddings   

# %%
projected_dataset_embeddings = project_embeddings(embeddings, umap_transform)

# %%
import matplotlib.pyplot as plt

plt.figure()
plt.scatter(projected_dataset_embeddings[:, 0], projected_dataset_embeddings[:, 1], s=10)
plt.gca().set_aspect('equal', 'datalim')
plt.title('Projected Embeddings')
plt.axis('off')

# %%
query = "What is the total revenue?"

results = chroma_collection.query(query_texts=query, n_results=5, include=['documents', 'embeddings'])

retrieved_documents = results['documents'][0]

for document in results['documents'][0]:
    print(document)
    print('')

# %%
query_embedding = embedding_function([query])[0]
retrieved_embeddings = results['embeddings'][0]

projected_query_embedding = project_embeddings([query_embedding], umap_transform)
projected_retrieved_embeddings = project_embeddings(retrieved_embeddings, umap_transform)


# %%
# Plot the projected query and retrieved documents in the embedding space
plt.figure()
plt.scatter(projected_dataset_embeddings[:, 0], projected_dataset_embeddings[:, 1], s=10, color='gray')
plt.scatter(projected_query_embedding[:, 0], projected_query_embedding[:, 1], s=150, marker='X', color='r')
plt.scatter(projected_retrieved_embeddings[:, 0], projected_retrieved_embeddings[:, 1], s=100, facecolors='none', edgecolors='g')

plt.gca().set_aspect('equal', 'datalim')
plt.title(f'{query}')
plt.axis('off')

# %%
query = "What is the strategy around artificial intelligence (AI) ?"
results = chroma_collection.query(query_texts=query, n_results=5, include=['documents', 'embeddings'])

retrieved_documents = results['documents'][0]

for document in results['documents'][0]:
    print(document)
    print('')

# %%
query_embedding = embedding_function([query])[0]
retrieved_embeddings = results['embeddings'][0]

projected_query_embedding = project_embeddings([query_embedding], umap_transform)
projected_retrieved_embeddings = project_embeddings(retrieved_embeddings, umap_transform)


# %%
# Plot the projected query and retrieved documents in the embedding space
plt.figure()
plt.scatter(projected_dataset_embeddings[:, 0], projected_dataset_embeddings[:, 1], s=10, color='gray')
plt.scatter(projected_query_embedding[:, 0], projected_query_embedding[:, 1], s=150, marker='X', color='r')
plt.scatter(projected_retrieved_embeddings[:, 0], projected_retrieved_embeddings[:, 1], s=100, facecolors='none', edgecolors='g')

plt.gca().set_aspect('equal', 'datalim')
plt.title(f'{query}')
plt.axis('off')

# %%
query = "What has been the investment in research and development?"
results = chroma_collection.query(query_texts=query, n_results=5, include=['documents', 'embeddings'])

retrieved_documents = results['documents'][0]

for document in results['documents'][0]:
    print(document)
    print('')

# %%
query_embedding = embedding_function([query])[0]
retrieved_embeddings = results['embeddings'][0]

projected_query_embedding = project_embeddings([query_embedding], umap_transform)
projected_retrieved_embeddings = project_embeddings(retrieved_embeddings, umap_transform)


# %%
# Plot the projected query and retrieved documents in the embedding space
plt.figure()
plt.scatter(projected_dataset_embeddings[:, 0], projected_dataset_embeddings[:, 1], s=10, color='gray')
plt.scatter(projected_query_embedding[:, 0], projected_query_embedding[:, 1], s=150, marker='X', color='r')
plt.scatter(projected_retrieved_embeddings[:, 0], projected_retrieved_embeddings[:, 1], s=100, facecolors='none', edgecolors='g')

plt.gca().set_aspect('equal', 'datalim')
plt.title(f'{query}')
plt.axis('off')

# %%
query = "What has Michael Jordan done for us lately?"
results = chroma_collection.query(query_texts=query, n_results=5, include=['documents', 'embeddings'])

retrieved_documents = results['documents'][0]

for document in results['documents'][0]:
    print(document)
    print('')

# %%
query_embedding = embedding_function([query])[0]
retrieved_embeddings = results['embeddings'][0]

projected_query_embedding = project_embeddings([query_embedding], umap_transform)
projected_retrieved_embeddings = project_embeddings(retrieved_embeddings, umap_transform)


# %%
# Plot the projected query and retrieved documents in the embedding space
plt.figure()
plt.scatter(projected_dataset_embeddings[:, 0], projected_dataset_embeddings[:, 1], s=10, color='gray')
plt.scatter(projected_query_embedding[:, 0], projected_query_embedding[:, 1], s=150, marker='X', color='r')
plt.scatter(projected_retrieved_embeddings[:, 0], projected_retrieved_embeddings[:, 1], s=100, facecolors='none', edgecolors='g')

plt.gca().set_aspect('equal', 'datalim')
plt.title(f'{query}')
plt.axis('off')

# %%
import requests

def get_bearer_token(wx_api_key):
    token_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {
        "apikey": wx_api_key,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    }
    response = requests.post(token_url, headers=headers, data=data)
    token = response.json()["access_token"]
    return token

def generate_answer(model, instruction, query, information, token):
    prompt = instruction
    input_txt = f"Question: {query}. Information: {information}"
    
    url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    data = {
        "model_id": model,
        "project_id": project_id,
        "input": prompt + '\n\n' + "Input: " + input_txt + "\n\n" + "Output: ",
        "parameters": {
            "decoding_method": "greedy",
            "min_new_tokens": 1,
            "max_new_tokens": 500,
            "beam_width": 1
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response = response.json()["results"][0]["generated_text"]
    
    return response

model = "meta-llama/llama-2-70b-chat"
instruction = "You are a helpful expert financial research assistant. Your users are asking questions about information contained in an annual report. You will be shown the user's question, and the relevant information from the annual report. Answer the user's question using only this information."

query = "What was the total revenue?"
results = chroma_collection.query(query_texts=[query], n_results=5)
retrieved_documents = results['documents'][0]

wx_api_key = WATSONX_APIKEY
wx_api_token = get_bearer_token(wx_api_key)

output = generate_answer(model, instruction, query, "\n\n".join(retrieved_documents), wx_api_token)

print(output)


# %%
# Generating Expanded Query by Concatenating Answer with Original Query
test_joint_query = f"{query} {output}"
print(test_joint_query)

# %%
import requests

def get_bearer_token(wx_api_key):
    token_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {
        "apikey": wx_api_key,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    }
    response = requests.post(token_url, headers=headers, data=data)
    token = response.json()["access_token"]
    return token

def generate_answer(model, instruction, query, information, token):
    prompt = instruction
    input_txt = f"Question: {query}. Information: {information}"
    
    url = "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    data = {
        "model_id": model,
        "project_id": project_id,
        "input": prompt + '\n\n' + "Input: " + input_txt + "\n\n" + "Output: ",
        "parameters": {
            "decoding_method": "greedy",
            "min_new_tokens": 1,
            "max_new_tokens": 500,
            "beam_width": 1
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response = response.json()["results"][0]["generated_text"]
    
    return response

model = "meta-llama/llama-2-70b-chat"
instruction = "You are a helpful expert financial research assistant. Your users are asking questions about information contained in an annual report. You will be shown the user's question, and the relevant information from the annual report. Answer the user's question using only this information."

query = test_joint_query
results = chroma_collection.query(query_texts=[query], n_results=5)
retrieved_documents = results['documents'][0]

wx_api_key = WATSONX_APIKEY
wx_api_token = get_bearer_token(wx_api_key)

output = generate_answer(model, instruction, query, "\n\n".join(retrieved_documents), wx_api_token)

print(output)


# %%
from nltk.corpus import wordnet

# Function to get synonyms of a word using WordNet
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace('_', ' '))
    return list(synonyms)

# Before Query Expansion
query = "What has been the investment in research and development?"
results_before = chroma_collection.query(query_texts=query, n_results=5, include=['documents', 'embeddings'])

retrieved_documents_before = results_before['documents'][0]

query_embedding_before = embedding_function([query])[0]
retrieved_embeddings_before = results_before['embeddings'][0]

projected_query_embedding_before = project_embeddings([query_embedding_before], umap_transform)
projected_retrieved_embeddings_before = project_embeddings(retrieved_embeddings_before, umap_transform)

# Plot before query expansion
plt.figure()
plt.scatter(projected_dataset_embeddings[:, 0], projected_dataset_embeddings[:, 1], s=10, color='gray')
plt.scatter(projected_query_embedding_before[:, 0], projected_query_embedding_before[:, 1], s=150, marker='X', color='r')
plt.scatter(projected_retrieved_embeddings_before[:, 0], projected_retrieved_embeddings_before[:, 1], s=100, facecolors='none', edgecolors='g')

plt.gca().set_aspect('equal', 'datalim')
plt.title(f'Before Query Expansion: {query}')
plt.axis('off')
plt.show()

# Synonym-based query expansion
# Split the original query into words
query_words = query.split()

# Get synonyms for each word in the query
expanded_query_words = []
for word in query_words:
    synonyms = get_synonyms(word)
    if synonyms:
        expanded_query_words.extend(synonyms)

# Combine the original query with synonyms
expanded_query = " ".join(expanded_query_words)

# After Query Expansion
results_after = chroma_collection.query(query_texts=expanded_query, n_results=5, include=['documents', 'embeddings'])

retrieved_documents_after = results_after['documents'][0]

query_embedding_after = embedding_function([expanded_query])[0]
retrieved_embeddings_after = results_after['embeddings'][0]

projected_query_embedding_after = project_embeddings([query_embedding_after], umap_transform)
projected_retrieved_embeddings_after = project_embeddings(retrieved_embeddings_after, umap_transform)

# Plot after query expansion
plt.figure(figsize=(8, 6))
plt.scatter(projected_dataset_embeddings[:, 0], projected_dataset_embeddings[:, 1], s=10, color='gray')
plt.scatter(projected_query_embedding_after[:, 0], projected_query_embedding_after[:, 1], s=150, marker='X', color='r')
plt.scatter(projected_retrieved_embeddings_after[:, 0], projected_retrieved_embeddings_after[:, 1], s=100, facecolors='none', edgecolors='g')

plt.gca().set_aspect('equal', 'datalim')
# plt.title(f'After Query Expansion:\n{expanded_query}', fontsize=12)
plt.axis('off')
plt.show()
