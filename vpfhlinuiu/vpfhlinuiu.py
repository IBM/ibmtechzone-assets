import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document, StorageContext
from llama_index.llms import OpenAI
#import openai
import os
import shutil
from llama_index import SimpleDirectoryReader
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM
from dotenv import load_dotenv
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index import download_loader
from glob import glob
from pymilvus import (connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)
from llama_index.vector_stores import MilvusVectorStore
from llama_index.node_parser import SentenceWindowNodeParser, HierarchicalNodeParser, get_leaf_nodes
from llama_index.postprocessor import MetadataReplacementPostProcessor

sentence_node_parser = SentenceWindowNodeParser.from_defaults(
    window_size=4,
    window_metadata_key="window",
    original_text_metadata_key="original_text"
)
postprocessor = MetadataReplacementPostProcessor(
    target_metadata_key="window",
)
#embed_model=HuggingFaceEmbedding(model_name='sentence-transformers/all-MiniLM-L12-v2')

# connections.connect(host="localhost", port="19530")
# collection_name="new_llama"
# if utility.has_collection(collection_name):
#     utility.drop_collection(collection_name)
# vectorstore=MilvusVectorStore(host="localhost",port="19530",dim=384,collection_name=collection_name)



############  ENV Details ######
env_path='/Users/vishwajithcr/Documents/envs/.envproj'
load_dotenv(dotenv_path=env_path)
collection_name="new_llama"

IBM_CLOUD_API_KEY = os.getenv("API_KEY", None)
WATSONX_AI_ENDPOINT = os.getenv("IBM_CLOUD_URL", None)
WX_PROJECT_ID = os.getenv("PROJECT_ID", None)

wx_credentials = {
    "url": WATSONX_AI_ENDPOINT,
    "apikey": IBM_CLOUD_API_KEY
}

parameters = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
    GenParams.MAX_NEW_TOKENS: 300,
    GenParams.MIN_NEW_TOKENS: 5,
    GenParams.TEMPERATURE: 0.2,
    "repetition_penalty": 1.3
    # GenParams.REPETITION_PENALTY: 2
    
    # GenParams.TOP_K: 50,
    # GenParams.TOP_P: 1
}


wx_model = Model(
    model_id=ModelTypes.LLAMA_2_70B_CHAT, 
    # model_id="ibm/granite-13b-instruct-v1",
    params=parameters, 
    credentials=wx_credentials,
    project_id=WX_PROJECT_ID)


watsonx_llm = WatsonxLLM(model=wx_model)

save_dir = 'uploaded_files'
# Ensure the directory exists

if os.path.exists(save_dir):
    # Delete all files and folders in the directory
    shutil.rmtree(save_dir)

# Create the directory
os.makedirs(save_dir)

system_prompt="""<s>[INST] <<SYS>>
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
<</SYS>>
You are given a document to analyse and answer the question please make sure you follow the following instructions
1. Please give the answer in not more than 2 sesntences, 
2. Donot provide the context of the question asked,
3. If you are not able to answer based on the question please answer "I donot Know" or ask for clarity, Donot provide false information.
4. Donot mention the document information in your response.
5. Answer in bullet points wherever necessary.
[/INST]
Answer:
"""

st.set_page_config(page_title="Chat with the Watsonx docs, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
#openai.api_key = st.secrets.openai_key
st.title("Chat with the WatsonX 🤖, powered by LlamaIndex 💬🦙")

with st.sidebar:
    uploaded_files = st.file_uploader(label='Upload the file below!!', type=['pdf'], accept_multiple_files=True)
    options = ["Chat Engine", "Query Engine", "Retriever Engine"]
    selected_option = st.selectbox("Select the retriever Mechanism", options)
    option2=["Text_chunk", "Sentence_Embedding"]
    embedding_method = st.selectbox("Select the Embedding Mechanism", option2)

         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about the document Uploaded"}
    ]

@st.cache_resource(show_spinner=False)
def load_data(collection_name,embedding_method):
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        embed_model=HuggingFaceEmbedding(model_name='sentence-transformers/all-MiniLM-L12-v2')
        connections.connect(host="localhost", port="19530")
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
        docs = SimpleDirectoryReader(input_dir=f"./{save_dir}", recursive=True).load_data()
        vectorstore=MilvusVectorStore(host="localhost",port="19530",dim=384,collection_name=collection_name)
        storage_cont=StorageContext.from_defaults(vector_store=vectorstore)
        if embedding_method == "Text_chunk":
            service_context=ServiceContext.from_defaults(llm=watsonx_llm,embed_model=embed_model,system_prompt=system_prompt,chunk_size=400, chunk_overlap=50)
        elif embedding_method == "Sentence_Embedding":
            service_context = ServiceContext.from_defaults(llm=watsonx_llm, embed_model=embed_model, node_parser=sentence_node_parser,system_prompt=system_prompt)
    
        index=VectorStoreIndex.from_documents(documents=docs,storage_context=storage_cont,service_context=service_context)
        return index

    
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_name = os.path.join(save_dir, uploaded_file.name)
        with open(file_name, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        index=load_data(collection_name,embedding_method)
        dict1={"Chat Engine":index.as_chat_engine(),"Query Engine":index.as_query_engine(),"Retriever Engine":index.as_retriever()}
        engine=dict1[selected_option]

        if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
            #st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
            st.session_state.chat_engine = engine
                
           



        

    if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        for message in st.session_state.messages: # Display the prior chat messages
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # If last message is not from assistant, generate a new response
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chat_engine.chat(prompt)
                    st.write(response.response)
                    message = {"role": "assistant", "content": response.response}
                    st.session_state.messages.append(message) # Add response to message history
        if st.button("Clear All"):
                # Clears all st.cache_resource caches:
                st.cache_resource.clear()
                st.cache_data.clear()
                #st.session_state.clear()
                #st.chat_message.clear()
                st.session_state.conversation = None
                st.session_state.chat_history = None
