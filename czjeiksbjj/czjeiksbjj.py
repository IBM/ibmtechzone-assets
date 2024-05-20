from dotenv import load_dotenv
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import os
from langchain.llms.watsonxllm import WatsonxLLM
import yfinance as yf
from ibm_watson_machine_learning.foundation_models import Model


load_dotenv()

# url = os.getenv("IBM_CLOUD_URL", None)
# apikey = os.getenv("IBM_CLOUD_API_KEY", None)
# project_id = os.getenv("PROJECT_ID", None)

# WATSONX_APIKEY = os.getenv("WATSONX_APIKEY", None)
# creds = {
#     "url": url,
#     "apikey": apikey
# }


def get_ticker(question,url,apikey,project_id,WATSONX_APIKEY):
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 500,
        "min_new_tokens": 1,
        "repetition_penalty": 1
    }
    model_id = "meta-llama/llama-3-70b-instruct"

    ok = WatsonxLLM(model_id=model_id, url=url, params=parameters, project_id=project_id, apikey=WATSONX_APIKEY,verbose=True)
    #Compare IBM and AAPL stock on stock performance in last 1 year
    prompt_input =f"""
    <|begin_of_text|>
    <|start_header_id|>system<|end_header_id|>
    Extract the stock tickers from given query.it can be a single ticker or multiple tickers in a single query.

    Query:
    What is the price of TCS stock

    Stock ticker:
    TCS

    Query:
    can you compare TCS and INFY        

    Stock ticker:
    TCS,INFY

    Query:
    Can you give some information about ADANIPORTS

    Stock ticker:
    ADANIPORTS

    Query:
    can you compare IBM AND AAPL

    Stock ticker:
    ITC,TCS

    <|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    Query:
    {question}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    Stock ticker:
    """

    generated_response = ok.invoke(input=[prompt_input])

    # print(generated_response)
    # answer=generated_response
    list_of_tickers = str(generated_response).split(",")
    # print(list_of_tickers)
    return list_of_tickers


def get_ticker_info(list_of_tickers):
    ticker_info = []
    for ticker in list_of_tickers:
        ticker=ticker
        print(ticker)
        ticker_info.append(yf.Ticker(ticker).info)
    return ticker_info


def qa(ticker_info,question,url,apikey,project_id,WATSONX_APIKEY,creds):
    prompt_input1=f"""
    <|begin_of_text|>
    <|start_header_id|>system<|end_header_id|>
    Below are a series of dialogues between various people and an AI assistant. The AI tries to be helpful, polite, honest, sophisticated, emotionally aware, and humble-but-knowledgeable. The assistant is happy to help with almost anything, and will do its best to understand exactly what is needed. It also tries to avoid giving false or misleading information, and it caveats when it isn't entirely sure about the right answer. Moreover, the assistant prioritizes caution over usefulness, refusing to answer questions that it considers unsafe, immoral, unethical or dangerous.
    Ill provide you with json data and answer me questions according to that pls give summarised answers
    '''{ticker_info}'''
    <|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    query: {question}
    <|eot_id|>
    <|start_header_id|>Assistant<|end_header_id|>
    Assistant:
    """
    parameters2 = {
        "decoding_method": "greedy",
        "repetition_penalty": 1.2,
        "max_new_tokens": 500,
        
    }
    model_id2 = "meta-llama/llama-3-70b-instruct"
    model2 = Model(
        model_id = model_id2,
        params = parameters2,
        credentials = creds,
        project_id = project_id
        )
    generated_response1 = model2.generate_text(prompt=prompt_input1)
    print(generated_response1)
    return generated_response1

def main():
    question = os.environ["question"]
    # question=input("Enter the query")
    url = os.environ["url"]
    apikey = os.environ["apikey"]
    project_id = os.environ["project_id"]
    WATSONX_APIKEY = apikey
    creds = {
        "url": url,
        "apikey": apikey
    }
    list_of_tickers = get_ticker(question,url,apikey,project_id,WATSONX_APIKEY)
    ticker_info = get_ticker_info(list_of_tickers)
    answer = qa(ticker_info,question,url,apikey,project_id,WATSONX_APIKEY,creds)
    return answer


if __name__ == "__main__":
    main()