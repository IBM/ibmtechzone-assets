import streamlit as st
from streamlit.web import cli as stcli
from streamlit import runtime

from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.extensions.langchain import (
    WatsonxLLM,
)
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

import pandas as pd

import openpyxl

import sys

st.set_page_config(
    page_title="QnA with Dataframe",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initilize_session_state(var):
    if var not in st.session_state:
        st.session_state[var] = None


def load_file(file):
    extension = file.name.split(".")[-1]

    if extension == "csv":
        df = pd.read_csv(file.name)
    elif extension == "xlsx":
        xl_file = openpyxl.open("ipl_2022.xlsx")
        sheet_names = xl_file.sheetnames

        sheet_name = st.selectbox("Select Sheet", options=sheet_names)
        df = pd.read_excel(file.name, sheet_name=sheet_name)

    return df


with st.sidebar:
    api_key = st.text_input(
        "Watsonx.ai API Key",
        type="password",
        help="WatsonX.ai API key",
        value="8lzuqCQlXFLDuQSKoMxocfgpHIQIbLU4YxWiislYPmjM",
    )
    cloud_url = st.text_input(
        "Watsonx Cloud URL",
        value="https://us-south.ml.cloud.ibm.com/",
        help="IBM Cloud URL",
    )
    project_id = st.text_input(
        "Watsonx.ai Project ID",
        help="WatsonX.ai project id",
        value="7629055d-8e95-4c3a-9ca4-de781b2a165b",
    )

    initilize_session_state("api_key")
    initilize_session_state("cloud_url")
    initilize_session_state("project_id")

    if api_key:
        st.session_state.api_key = api_key
    if cloud_url:
        st.session_state.cloud_url = cloud_url
    if project_id:
        st.session_state.project_id = project_id

file = st.file_uploader(
    "Upload the Base Excel File",
    key="base_file",
    label_visibility="collapsed",
)

if file:
    if (
        st.session_state.api_key
        and st.session_state.cloud_url
        and st.session_state.project_id
    ):

        df = load_file(file)
        st.dataframe(df, hide_index=True, use_container_width=True, height=400)

        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 2000,
            "min_new_tokens": 1,
        }
        initilize_session_state("watsonx_llm")
        if not st.session_state.watsonx_llm:
            with st.spinner("Loading LLM..."):
                llm = Model(
                    model_id="meta-llama/llama-3-70b-instruct",
                    credentials={
                        "url": st.session_state.cloud_url,
                        "apikey": st.session_state.api_key,
                    },
                    project_id=st.session_state.project_id,
                    params=parameters,
                )
                st.session_state.watsonx_llm = WatsonxLLM(model=llm)

        pandas_agent = create_pandas_dataframe_agent(
            st.session_state.watsonx_llm, df, verbose=True
        )

        query = st.text_input("Query", help="Enter your query against your Dataframe")

        if query and st.button("Submit"):
            with st.spinner("Getting response"):
                response = pandas_agent(query)

            st.write(response["output"])
    else:
        st.warning("Kindly Provide Watsonx.ai credentials on sidebar.")

if __name__ == "__main__":
    if runtime.exists():
        print("Running ......")
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
