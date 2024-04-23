import os
import pandas as pd
from utils.functions import *
from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
load_dotenv()
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from genai.credentials import Credentials
from genai import Client
from genai.extensions.langchain import LangChainInterface
from genai import Credentials, Client, LangChainInterface, LLMChain, PromptTemplate

class DataSummarization:
    def __init__(self, data_file, api_key_env_var, api_endpoint, model_id, params):
        self.data_file = data_file
        self.data_df = pd.read_csv(data_file)
        self.bam_api_key = os.environ[api_key_env_var]
        self.bam_api_endpoint = api_endpoint
        self.model_id = model_id
        self.params = params
        self.client = self.init_client()
        self.llm = self.init_llm_interface()
        self.prompt = self.create_prompt_template()
        self.results_df = pd.DataFrame(columns=['Col_name'])

    def init_client(self):
        credentials = Credentials(api_key=self.bam_api_key, api_endpoint=self.bam_api_endpoint)
        return Client(credentials=credentials)

    def init_llm_interface(self):
        return LangChainInterface(model_id=self.model_id, parameters=self.params, client=self.client)

    def create_prompt_template(self):
        summary_prompt = (
        f"""
        <<SYS>>
        You are an expert at summarising the content in a given row, your job is to go through each column for that particular row and summarise the content by following the given steps below.
        <<SYS>>

        [INST]
        - First take a look at all the columns in the given row {{text}}.
        - Now create a text chunk that includes the data from all the columns.
        - The following are your columns of a particular row: 
        'Lighthouse ID ', 'Project Description', 'Engagement and Use Case Summary', 'Business Value and Proposition', 'Top Lessons Learned  (limit to 500 Characters)', 'Fail Forward - Engagement Details',
        'Failing Forward - References  - append to Fail Forward Details', 'Engagement Background',
        'Engagement Success', 'Stories / Narratives', 'Client Feedback  (limit to 500 Characters)',
        'Client Quote(s)', 'IBM Outcome  (limit to 500 Characters)', 'Next Steps For IBM',
        'Next Steps Discussed with the Client', 'Client Technology Landscape'
        - The above columns, is the format for the order in which data will be given to you for a corresponding row 
        - Now perform the summarisation on that chunk of text
        - While performing the summarisation, keep the logic intact and make sure the summary is done accordingly
        - Give me the Lighthouse ID associated in the output along with the summary 
        - Give me the Lighthouse ID in a separate line
        - Give the output in a legible manner 
        - Give me the summarised output 

        [/INST]
        reasoning 

        {{text}}
        reasoning:
                    """
        )

        return PromptTemplate(input_variables=["text"], template=summary_prompt)

    def process_data(self):
        for _, row in self.data_df.iterrows():
            text = ' '.join([str(value) for value in row])
            description = self.invoke_llm(text)
            print(description)
            self.results_df = self.results_df.append({'Col_name': description}, ignore_index=True)

    def invoke_llm(self, text):
        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        return chain.invoke({'text': text}).get('text')

    def save_results(self, filename):
        self.results_df.to_csv(filename, index=False)

    def run(self):
        self.process_data()
        self.save_results("summary.csv")

# Example usage
if __name__ == "__main__":
    data_summarization = DataSummarization(
        data_file="data.csv",
        api_key_env_var="bam_api_key",
        api_endpoint="https://bam-api.res.ibm.com",
        model_id="mistralai/mistral-7b-instruct-v0-2",
        params={
            "decoding_method": "greedy",
            "max_new_tokens": 4000,
            "min_new_tokens": 50,
            "top_k": 100,
            "top_p": 1,
            "temperature": 0
        }
    )
    data_summarization.run()
