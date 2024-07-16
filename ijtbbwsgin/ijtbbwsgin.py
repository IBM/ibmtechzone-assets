import pandas as pd
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_ibm import WatsonxLLM
from langchain_community.agent_toolkits import create_sql_agent

# Load DataFrame
df = pd.read_csv("cognos_preprocessed.csv")
print(df.shape)
print(df.columns.tolist())

# Create SQLite engine and save DataFrame to SQL
engine = create_engine("sqlite:///duskinV1.db")
df.to_sql("duskinV1", engine, index=False)

# Setup SQLDatabase
db = SQLDatabase(engine=engine)
print(db.dialect)
print(db.get_usable_table_names())

# WatsonxLLM setup
api_key = '_yUkax1ui_NJRP1lJgdq6rPUXnTANcTFNrzNyDuZEIeU'
project_id = 'd074757e-bc9d-4a6e-881c-5af3a040294a'
parameters = {
    "decoding_method": "sample",
    "max_new_tokens": 100,
    "min_new_tokens": 1,
    "temperature": 0.5,
    "top_k": 50,
    "top_p": 1,
}

watsonx_llm = WatsonxLLM(
    model_id="ibm/granite-13b-instruct-v2",
    url="https://us-south.ml.cloud.ibm.com",
    project_id=project_id,
    params=parameters,
    apikey=api_key
)

# Prompt template
template = """
Given the following question, generate a valid SQL query.

Question: {input}

Table: duskin
Columns: {columns}
"""

columns = ", ".join(df.columns.tolist())
prompt = PromptTemplate(input_variables=["input", "columns"], template=template)

# Create and run SQL agent
agent_executor = create_sql_agent(watsonx_llm, db=db, verbose=True, handle_parsing_errors=True)
query = prompt.format(input="what's the average Total Sales for August", columns=columns)
result = agent_executor.invoke({"input": query})
print(result)
