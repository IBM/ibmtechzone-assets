from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import os
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
import pandas as pd
import gradio as gr
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import requests
import re
pd.options.mode.copy_on_write = True
os.environ['KMP_DUPLICATE_LIB_OK']='True'
os.environ['TOKENIZERS_PARALLELISM']='false'
embedding = HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-large-instruct')

api_key =os.environ["api_key"]
project_id= os.environ["project_id"]
model_params = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 100,
    GenParams.RANDOM_SEED: 42,
    GenParams.TEMPERATURE: 0,
    GenParams.REPETITION_PENALTY: 1.0,
    GenParams.STOP_SEQUENCES:["\n\n"]
}
# mistralai/mixtral-8x7b-instruct-v01
# ibm/granite-13b-chat-v2
model = WatsonxLLM(
    cache=True,
    model_id="meta-llama/llama-3-70b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    project_id="7671c6cc-539c-4dce-b8c4-18dc4088bd68",
    params=model_params,
)


llm=model
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=180)
# memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm, 
    memory = memory,
    # verbose=True
)
memory.save_context({"input": "Hello"}, 
                    {"output": "How are you, how can I help?"})
                    
memory.save_context({"input": "What is the weather like today?"}, 
                    {"output": "It's sunny and warm today."})

memory.save_context({"input": "Can you recommend a good book?"}, 
                    {"output": "I recommend 'To Kill a Mockingbird' by Harper Lee."})

memory.save_context({"input": "How do I make a cake?"}, 
                    {"output": "You will need flour, sugar, eggs, and butter. Mix and bake at 350°F for 30 minutes."})

memory.save_context({"input": "What's the capital of France?"}, 
                    {"output": "The capital of France is Paris."})

memory.save_context({"input": "What is 2 + 2?"}, 
                    {"output": "2 + 2 equals 4."})

memory.save_context({"input": "Who wrote '1984'?"}, 
                    {"output": "'1984' was written by George Orwell."})

memory.save_context({"input": "What's the latest news?"}, 
                    {"output": "Today's top news is about the upcoming elections."})

memory.save_context({"input": "Can you play music?"}, 
                    {"output": "Sure, what song would you like to hear?"})

memory.save_context({"input": "How do I get to the nearest hospital?"}, 
                    {"output": "The nearest hospital is 2 miles away, take the second left and go straight."})

memory.save_context({"input": "What's the best way to learn Python?"}, 
                    {"output": "The best way to learn Python is through practice and online resources like Codecademy and Coursera."})

def make_prompt(context, question_text):
    return (
        f"Question: {question_text}?\n"
        f"You need to extract the exact and complete answer for the question.\n"
        f"Use the Context below to find the answer for the question above:\n"
        f"Avoid special characters if not needed"
        f"Your OUTPUT SHOULD BE IN JAPANESE LANGUAGE"
    )
previous_summary=""
def chat_interaction(message, chat_history):
    chat_history=[]
    cache = get_llm_cache()
    global previous_summary
    cached_response = cache.lookup(message, "")
    # if cached_response is not None:
    #     print("Response found in cache.")
    #     return cached_response
    
    # df1 = search(message, 5)
    # print(df1.columns)
    # document_texts = df1["回答内容"].tolist() + df1["回答備考"].tolist()

    # document_texts = [text for text in document_texts if pd.notna(text)]

    # context = "\n\n\n".join(document_texts)

    prompt = make_promp(message)

    # input_list = [{"input": message, "history": chat_history, "text": prompt}]

    response = conversation.invoke(prompt)

    cache.update(message, "", response['response'])

    chat_history.append(("Assistant", response['response']))

    memory.save_context({"input": message}, {"output": response['response']})
    
    messages = memory.chat_memory.messages
    print("messages:",messages)
    summary = memory.predict_new_summary(messages, previous_summary)
    print("Summary Here----",summary)

    return response['response']
    
    memory.save_context({"input": "Hello"}, 
                    {"output": "How are you, how can I help?"})
chat_history=[]
chat_interaction(message="Hello",chat_history=chat_history)