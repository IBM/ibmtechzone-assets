import os
from langchain_ibm import WatsonxLLM
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 100,
    "min_new_tokens": 1,
    "temperature": 0,
    "repetition_penalty": 1
}

wx_api_key = os.environ["wx_api_key"]
project_id = os.environ["project_id"]
cloud_url = os.environ["ibm_cloud_url"]


model = WatsonxLLM(
            model_id="meta-llama/llama-3-70b-instruct",
            #model_id="ibm-mistralai/mixtral-8x7b-instruct-v01-q",
            url=cloud_url,
            project_id=project_id,
            params=parameters,
            apikey=wx_api_key,
            verbose=True
        )

def call_string_output_parser():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Tell me a joke about the following subject"),
        ("human", "{input}")
    ])
    
    parser = StrOutputParser()

    chain = prompt | model | parser

    return chain.invoke({
        "input":"IBM WatsonX"
        })

def call_list_output_parser():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate a python list of 10 synonyms for the following word. Return the results only as a comma seperated list. "),
        ("human", "{input}")
    ])

    parser = CommaSeparatedListOutputParser()

    chain = prompt | model | parser

    return chain.invoke({
        "input": "happy"
    })

print("Example of string output parser", type(call_string_output_parser()))
print(call_string_output_parser())

print("Example of List output parser", type(call_list_output_parser()))
print(call_list_output_parser())
