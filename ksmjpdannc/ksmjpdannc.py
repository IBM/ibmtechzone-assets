# Building a Router Engine for RAG use case using llama_index

# This notebook depicts how to create and use router engine for building an agentic-RAG pipeline for two use cases summarization and question answering. The integration involves llama_index library integrated with BAM.

# requirements file
#  note which revision of python, for example 3.9.6
#  in this file, insert all the pip install needs, include revision


# python-dotenv==1.0.0

# llama-index==0.10.27
# llama-index-llms-openai==0.1.15
# llama-index-embeddings-openai==0.1.7

import os

import nest_asyncio

nest_asyncio.apply()


# Load data
# Just put the pdf or list of pdf's inside the input_files list 

from llama_index.core import SimpleDirectoryReader

# load documents
file_name = os.environ["file_name"]
documents = SimpleDirectoryReader(input_files=file_name).load_data()

# Define LLM and Embedding model

from llama_index.core.node_parser import SentenceSplitter

splitter = SentenceSplitter(chunk_size=1024)
nodes = splitter.get_nodes_from_documents(documents)

# Setting up LLM

from dotenv import load_dotenv
from llama_index.core import Settings

from genai import Client
from genai.credentials import Credentials
from genai.extensions.llama_index import IBMGenAILlamaIndex
from genai.schema import DecodingMethod, TextGenerationParameters

# make sure you have a .env file under genai root with
# GENAI_KEY=<your-genai-key>
load_dotenv()

def heading(text: str) -> str:
    """Helper function for centering text."""
    return "\n" + f" {text} ".center(80, "=") + "\n"

client = Client(credentials=Credentials.from_env())

llm = IBMGenAILlamaIndex(
    client=client,
    model_id="meta-llama/llama-3-8b-instruct",
    parameters=TextGenerationParameters(
        decoding_method=DecodingMethod.SAMPLE,
        max_new_tokens=100,
        min_new_tokens=10,
        temperature=0.5,
        top_k=50,
        top_p=1,
    ),
)

Settings.llm = llm


# Setting up Embedding model

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)


# Define Summary Index and Vector Index over the Same Data

from llama_index.core import SummaryIndex, VectorStoreIndex

summary_index = SummaryIndex(nodes)
vector_index = VectorStoreIndex(nodes)

# Define Query Engines and Set Metadata

summary_query_engine = summary_index.as_query_engine(
    response_mode="tree_summarize",
    use_async=True,
)
vector_query_engine = vector_index.as_query_engine()

from llama_index.core.tools import QueryEngineTool


summary_tool = QueryEngineTool.from_defaults(
    query_engine=summary_query_engine,
    description=(
        "Useful for summarization questions related to document"
    ),
)

vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_query_engine,
    description=(
        "Useful for retrieving specific context from the document."
    ),
)

# Define Router Query Engine

from llama_index.core.query_engine.router_query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector


query_engine = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[
        summary_tool,
        vector_tool,
    ],
    verbose=True
)


import pandas as pd
import time



def generate_responses_to_questions(questions):
    """
    Takes a list of questions, passes them to the LlamaIndex Router Query Engine,
    generates responses, stores the questions, responses, and routing information
    in a pandas DataFrame, and exports it to an Excel file.
    
    Args:
        questions (list): A list of questions to be answered by the LLM.
    
    Returns:
        A pandas DataFrame containing the questions, their corresponding responses, and routing information.
    """
    
    # Create an empty list to store question-response-routing tuples
    qa_pairs = []
    
    # Loop through each question
    for question in questions:
        start_time = time.time()
        
        # Generate response from the LLM
        response = query_engine.query(question)
        
        # Stop the timer and calculate the elapsed time
        end_time = time.time()
        response_time = end_time - start_time
        
        # Extract the response text and routing information
        response_text = response.response
        routing_info = str(response.metadata['selector_result'].selections[0].index) +':'+ str(response.metadata['selector_result'].reason)

        
        # Append the question-response-routing tuple to the list
        qa_pairs.append({"Question": question, "Response": response_text, "Routing": routing_info, 'Time_taken':response_time})
    
    # Create a DataFrame from the question-response-routing pairs
    df = pd.DataFrame(qa_pairs)
    
    # Export the DataFrame to an Excel file
    df.to_excel("questions_and_responses.xlsx", index=False)
    

    return df

# add the list_of_questions and the function will return a dataframe with questions and responses generated with other information such as routing_info and time taken for each iteration.


list_of_questions = []
df = generate_responses_to_questions(list_of_questions)
#print(df)
