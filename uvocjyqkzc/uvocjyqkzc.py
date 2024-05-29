import os
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from langchain.prompts import PromptTemplate

#config Watsonx.ai environment
api_key = os.environ("api_key", None)
ibm_cloud_url = os.environ("ibm_cloud_url", None)
project_id = os.environ("project_id", None)

if api_key is None or ibm_cloud_url is None or project_id is None:
    raise Exception("Ensure you copied the .env file that you created earlier into the same directory as this notebook")
else:
    creds = {
        "url": ibm_cloud_url,
        "apikey": api_key 
    }

def send_to_watsonxai(prompt, model_name="codellama/codellama-34b-instruct-hf"):
    model_params = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.MAX_NEW_TOKENS: 400,
            GenParams.STOP_SEQUENCES:[";"]
        }
    
    # Instantiate a model proxy object to send your requests
    model = Model(
        model_id=model_name,
        params=model_params,
        credentials=creds,
        project_id=project_id)
    
    llm_response = model.generate_text(prompt)
    return llm_response

prompt_pattern = """Your task is to generate SQL queries that will be used to pull data from one tables in a DB2 database. The schema for the table with description of each column is:

sql CREATE TABLE INVOICE_TABLE(
Name of the article sold: ARTICLE_NAME     VARCHAR(50),
Amount at which article was bought: COST_INCURRED     NUMERIC,
Amount at which article was sold: PRICE_SOLD     NUMERIC,
Date article was sold: DATE_SOLD     DATE,
City where sold: CITY     VARCHAR(20),
Customer Name sold to: CUSTOMER_NAME     VARCHAR(20)
);

Examples:
Input: List all the articles where there was a loss.
Output: SELECT * FROM INVOICE_TABLE WHERE COST_INCURRED > PRICE_SOLD;

Input: How many articles were sold to MKV?
Output: SELECT COUNT(*) AS "Number of Articles Sold to MKV" FROM INVOICE_TABLE WHERE CUSTOMER_NAME == "MKV";

Input: {Question}
Output:

"""

prompt_template = PromptTemplate.from_template(prompt_pattern)

question = os.environ("question", None)
if question:
    prompt = prompt_template.format(Question = question)
    response = send_to_watsonxai(prompt=prompt)
    print(response.strip())
else:
    response = "No Valid Input"