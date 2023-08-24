import pandas as pd
import pandas_profiling
import streamlit as st
from sqlalchemy import create_engine
from streamlit_pandas_profiling import st_profile_report

CONN_STRING = os.environ["conn_string"]
TABLE_NAME = os.environ["table_name"]
query="SELECT * FROM "+TABLE_NAME

my_conn = create_engine(CONN_STRING)

df = pd.read_sql(query,my_conn)
pr = df.profile_report()

st_profile_report(pr)