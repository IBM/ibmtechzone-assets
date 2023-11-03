# app.py, run with 'streamlit run app.py'
import pandas as pd
import streamlit as st
FILE_NAME = os.environ["file_name"]
df = pd.read_csv(FILE_NAME)  # read a CSV file inside the 'data" folder next to 'app.py'
# df = pd.read_excel(...)  # will work for Excel files

st.title("My CSV file!")  # add a title
st.write(df)  # visualize my dataframe in the Streamlit app