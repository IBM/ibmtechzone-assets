import streamlit as st
from streamlit.web import cli as stcli
from streamlit import runtime

import pandas as pd
import numpy as np
import json

import sqlite3

from ibm_watson_machine_learning.foundation_models import Model

import re
import os
from dotenv import load_dotenv

pwd = os.getcwd()
env_path = os.path.join(pwd, ".env")
load_dotenv(env_path)

st.set_page_config(
    page_title="Chat with Excel",
    layout="wide",
    initial_sidebar_state="expanded",
)


class QueryLLM:
    def __init__(self, model_name, parameters) -> None:
        self.api_key = st.session_state.api_key
        self.api_url = st.session_state.cloud_url
        self.project_id = st.session_state.project_id
        print(st.session_state.api_key)
        print(st.session_state.cloud_url)
        print(st.session_state.project_id)

        self.model_id = model_name

        self.parameters = parameters

        self.model = Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials={"url": self.api_url, "apikey": self.api_key},
            project_id=self.project_id,
        )

    def query_llm(self, prompt, stream=False):
        print("=" * 100, "Quering LLM", "=" * 100)
        if stream:
            return self.model.generate_text_stream(prompt)
        else:
            return self.model.generate_text(prompt)

    def detailed_query_llm(self, prompt):
        print("=" * 100, "Quering LLM", "=" * 100)

        return self.model.generate(prompt)


def load_file(file):
    extension = file.name.split(".")[-1]

    if extension == "csv":
        df = pd.read_csv(file.name)
    elif extension == "xlsx":
        df = pd.read_excel(file.name)

    return df


def format_column_details(value_dict):
    print(value_dict, type(value_dict))
    details = ""

    for k, v in value_dict.items():
        details = details + "\n" + f"{k}: {v}"

    return details.strip()


def format_few_shots(value_dict):
    print(value_dict, type(value_dict))
    details = ""

    for k, v in value_dict.items():

        if not v.lower().startswith("<sql>"):
            v = "<SQL>" + v

        if not v.lower().endswith("</sql>"):
            v = v + "</SQL>"

        v = v.replace("\n", "\\n")
        details = (
            details
            + "\n\n"
            + f"""Question: {k}
Query: {v}"""
        )

    return details.strip()


def initilize_session_state(session_state_varriable):
    print(session_state_varriable, type(session_state_varriable))
    if session_state_varriable not in st.session_state:
        st.session_state[session_state_varriable] = None


def query_sql(sql_query):

    with st.session_state.conn:
        st.session_state.cur.execute(sql_query)
        headers = [description[0] for description in st.session_state.cur.description]
        rows = st.session_state.cur.fetchall()
        rows_df = []
        for row in rows:
            rows_df.append(row)
        print(f"{rows=}")
        sql_result = pd.DataFrame(rows, columns=headers)
        print(sql_result)
        print(type(sql_result))

    return sql_result


with st.sidebar:
    api_key = st.text_input(
        "Watsonx.ai API Key",
        type="password",
        help="WatsonX.ai API key",
    )
    cloud_url = st.text_input(
        "Watsonx Cloud URL",
        value="https://us-south.ml.cloud.ibm.com/",
        help="IBM Cloud URL",
    )
    project_id = st.text_input("Watsonx.ai Project ID", help="WatsonX.ai project id")

    initilize_session_state("api_key")
    initilize_session_state("cloud_url")
    initilize_session_state("project_id")

    if api_key:
        st.session_state.api_key = api_key
    if cloud_url:
        st.session_state.cloud_url = cloud_url
    if project_id:
        st.session_state.project_id = project_id

    db_name = "DB1"
    table_name = "sql_table"

input_file = st.file_uploader(
    "Upload your Excel or CSV file",
    type=["xlsx", "csv"],
    help="Supports Excel and CSV file.",
)

if input_file:

    df = load_file(input_file)

    initilize_session_state("db")

    if db_name and table_name:
        if not st.session_state.db:
            st.session_state.db = True

            if db_name.split(".")[-1].lower() != "db":
                db_name = f"{db_name}.db"

            initilize_session_state("conn")
            initilize_session_state("cur")
            conn = sqlite3.connect(db_name)
            cur = conn.cursor()
            if conn:
                st.session_state.conn = conn
                st.session_state.cur = cur
            with st.session_state.conn:

                sqlite_type_mapping = {
                    "object": "TEXT",
                    "int64": "INTEGER",
                    "float64": "REAL",
                    "datetime64[ns]": "DATETIME",
                    "datetime64[ns, UTC]": "TIMESTAMP",
                    "timedelta64[ns]": "TEXT",  # Convert timedelta to text for now
                }

                columns_with_types = ", ".join(
                    [
                        f"{col} {sqlite_type_mapping.get(str(df[col].dtype), 'TEXT')}"
                        for col in df.columns
                    ]
                )

                create_query = (
                    f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})"
                )
                create_table_query = create_query
                print(create_query)
                cur.execute(create_table_query)

                df.to_sql(table_name, conn, if_exists="replace")

                ddl_query = f"SELECT sql FROM sqlite_master WHERE name='{table_name}' AND type='table'"
                cur.execute(ddl_query)
                table_schema = cur.fetchone()[0]

                st.session_state.table_schema = table_schema

        initilize_session_state("column_details")
        if api_key and cloud_url and project_id:

            params = {
                "decoding_method": "greedy",
                "max_new_tokens": 500,
                "min_new_tokens": 0,
                "stop_sequences": [],
                "repetition_penalty": 1,
            }
            initilize_session_state("llm")
            # llm = QueryLLM("ibm-mistralai/mixtral-8x7b-instruct-v01-q", params)
            if not st.session_state.llm:
                llm = QueryLLM("meta-llama/llama-3-70b-instruct", params)
                st.session_state.llm = llm

            st.write("Provide Column details: ")
            tabs_1 = st.tabs(["as JSON", "as Fields", "as Excel or CSV"])

            with tabs_1[0]:
                column_details = st.text_area(
                    "Column Details as JSON",
                    height=300,
                    help="Provide column name and description pairs",
                )

                try:
                    if column_details:
                        column_details_dict = json.loads(column_details)
                        if column_details_dict:
                            st.session_state.column_details = column_details_dict
                except Exception as e:
                    print(e)
                    st.error(
                        "Kindly provide a valid json of column name and description pairs"
                    )
            with tabs_1[1]:

                with st.form("Column Details"):
                    size = st.number_input(
                        "Number of column details to be added", step=1, value=3
                    )
                    if size:
                        df = pd.DataFrame(
                            {
                                "columns": [f"" for i in range(size)],
                                "descriptions": [f"" for i in range(size)],
                            }
                        )
                        edited_df = st.data_editor(df, use_container_width=True)

                    form1_submit = st.form_submit_button()
                    if form1_submit:
                        print("edited df", edited_df)
                        st.session_state["column_details_df"] = edited_df.replace(
                            ["", " "], np.nan
                        )
                        st.session_state.column_details_df = (
                            st.session_state.column_details_df.dropna()
                        )

                        st.session_state.column_details = {
                            r["columns"]: r["descriptions"]
                            for i, r in st.session_state.column_details_df.iterrows()
                        }
                        st.write("Your loaded column details")
                        st.json(st.session_state.column_details)

            with tabs_1[2]:
                column_details_file = st.file_uploader(
                    "Upload your Excel or CSV file of column details",
                    type=["xlsx", "csv"],
                )
                if column_details_file:
                    column_details_df = load_file(column_details_file)
                    headers = [i.lower() for i in list(column_details_df.columns)]
                    if "columns" in headers and "descriptions" in headers:
                        st.session_state["column_details_df"] = (
                            column_details_df.replace(["", " "], np.nan)
                        )
                        st.session_state.column_details_df = (
                            st.session_state.column_details_df.dropna()
                        )

                        st.session_state.column_details = {
                            r["columns"]: r["descriptions"]
                            for i, r in st.session_state.column_details_df.iterrows()
                        }

                        st.write("Your loaded column details")

                        st.json(st.session_state.column_details)
                    else:
                        st.error(
                            'Make sure your file has headers "columns" and "descriptions"'
                        )

            addl_details = st.text_area(
                "Additional Details",
                help="Provide the details about your data, if any abbreviation or aliases present in the data. Use bullet points.",
            )

            if addl_details:
                st.session_state.additional_details = addl_details

            st.write("Provide Few Shots Examples: ")
            tabs_2 = st.tabs(["as JSON", "as Fields", "as Excel or CSV"])

            with tabs_2[0]:
                few_shots = st.text_area(
                    "Few Shots as JSON",
                    height=300,
                    help="Provide question and SQL query pairs",
                )

                initilize_session_state("few_shots")
                try:
                    if few_shots:
                        few_shots_dict = json.loads(few_shots)
                        if column_details_dict:
                            st.session_state.few_shots = few_shots_dict
                except Exception as e:
                    print(e)
                    st.error(
                        "Kindly provide a valid json of column question and SQL query pairs"
                    )

            with tabs_2[1]:

                with st.form("Provide few shots examples"):
                    size = st.number_input(
                        "How many few shot example you want to add?", step=1, value=3
                    )
                    if size:
                        df = pd.DataFrame(
                            {
                                "questions": [f"" for i in range(size)],
                                "sql_queries": [f"" for i in range(size)],
                            }
                        )
                        edited_df = st.data_editor(df, use_container_width=True)

                    form1_submit = st.form_submit_button()
                    if form1_submit:
                        st.session_state["few_shots_df"] = edited_df.replace(
                            ["", " "], np.nan
                        )
                        st.session_state.few_shots_df = (
                            st.session_state.few_shots_df.dropna()
                        )

                        st.session_state.few_shots = {
                            r["questions"]: r["sql_queries"]
                            for i, r in st.session_state.few_shots_df.iterrows()
                        }
                        st.write("Your loaded few shots examples")
                        st.json(st.session_state.few_shots)

            with tabs_2[2]:

                few_shots_file = st.file_uploader(
                    "Upload your Excel or CSV file with few shot examples",
                    type=["xlsx", "csv"],
                )
                if few_shots_file:
                    few_shots_df = load_file(few_shots_file)
                    headers = [i.lower() for i in list(few_shots_df.columns)]
                    if "questions" in headers and "descriptions" in headers:
                        st.session_state["few_shots_df"] = few_shots_df.replace(
                            ["", " "], np.nan
                        )
                        st.session_state.few_shots_df = (
                            st.session_state.few_shots_df.dropna()
                        )

                        st.session_state.few_shots = {
                            r["questions"]: r["sql_queries"]
                            for i, r in st.session_state.few_shots_df.iterrows()
                        }
                        st.write("Your loaded few shots examples")
                        st.json(st.session_state.few_shots)
                    else:
                        st.error(
                            'Make sure your file has headers "questions" and "sql_queries"'
                        )

            st.session_state.prompt_template = '''Given an input question, use sqlite syntax to generate a sql query for the following table. Write query in between <SQL></SQL>. No additional text or no explanation needed.

Avoid creating "DELETE", "DROP", "ALTER", "TRUNCATE" queries even if asked for. Create only and only "SELECT" queries.

For this Problem you can use the following table Schema:
<table_schema>
{table_schema}
</table_schema>

Columns Details: """
{column_details}
"""

{additional_details}

Examples:
{few_shots}
            
Please provide the SQL query for this question: 
Question: {input}
Query: '''

            if st.session_state.column_details:
                formated_column_details = format_column_details(
                    st.session_state.column_details
                )
            else:
                formated_column_details = ""

            if st.session_state.few_shots:
                formated_few_shots = format_few_shots(st.session_state.few_shots)
            else:
                formated_few_shots = ""
            print(formated_column_details)

            query = st.text_input("Question")

            if query:
                prompt = st.session_state.prompt_template.format(
                    input=query,
                    table_schema=st.session_state.table_schema,
                    column_details=formated_column_details,
                    few_shots=formated_few_shots,
                    additional_details=st.session_state.additional_details,
                )

                st.write("Your Prompt")
                with st.container(height=400):
                    st.code(prompt)

                response = st.session_state.llm.query_llm(prompt)

                print(f"{response=}")

                pattern = r"<SQL>(.*?)</SQL>"

                st.write("Generated SQL")
                match = re.findall(pattern, response.strip(), re.DOTALL)
                response = match[0].strip()
                st.code(response)

                with st.session_state.conn:

                    sql_result = query_sql(response)

                    st.write("Result from table")
                    st.dataframe(sql_result)

                    sql_result = sql_result.to_markdown(index=False)

                    final_prompt_template = '''Provide a clear and concise answer to the below asked question based on the information from the database. The response should be no more than 2-3 sentences, \
and should directly address the key points of the query. Avoid unnecessary details or contextual information not directly relevant to the question.

Question: """{question}"""

Result from DB: 
"""
{sql_result}
"""

Answer: '''
                    final_prompt = final_prompt_template.format(
                        question=query, sql_result=sql_result
                    )

                    final_response = st.session_state.llm.query_llm(final_prompt)

                    st.write("Answer")
                    st.write(final_response)
                    
                    
if __name__ == '__main__':
    if runtime.exists():
        print("Running ......")
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
