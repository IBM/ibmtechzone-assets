# Authors: Pinkal Patel
# pip install streamlit;pip install pandas
'''
Title : Selenium Project Discovery and Refactor Test Code

Description:
In this project, Code analyzes the selenium test case java project as a whole folder and extracts the test file with its dependency. 
Input: Selenium Project
Output: Display table as test files with dependency and also stored into CSV file.
'''

import pandas as pd
import streamlit as st
import sys
from streamlit.web import cli as stcli
from streamlit import runtime
from streamlit.components.v1 import html
from discovery_refactore_selenium_code import code_discovery_and_refactore
import os
cwd = os.getcwd()

st.title("Selenium Project Discovery and Refactor The Code")

if runtime.exists():
    with st.form("my-form", clear_on_submit=True):
        selenium_project_path = st.text_input("Enter output path:", cwd+"/java-selenium")
        submitted = st.form_submit_button("Analyze")

    if selenium_project_path:
        with st.spinner("Discovery and Refactoring..."):
            if not 'test_files_with_dependency' in st.session_state:
                    st.session_state.test_files_with_dependency = code_discovery_and_refactore(selenium_project_path)
                    if 'test_files_with_dependency' in st.session_state:
                        print("st.session_state.test_files_with_dependency: ",st.session_state.test_files_with_dependency)
                    st.success("Project Discovery and Refactor successfully!")
            st.text("") # Empty space for separation

    if 'test_files_with_dependency' in st.session_state:
        data = []
        for key_path in st.session_state.test_files_with_dependency:
            #print("Main File:",key_path)
            #print("Dependent File: \n")
            temp_dep_files = []
            for dep_file in st.session_state.test_files_with_dependency[key_path]:
                temp_dep_files.append(dep_file.split('/')[-1])
            data.append([key_path.split('/')[-1],temp_dep_files,key_path,st.session_state.test_files_with_dependency[key_path]])

        dep_df = pd.DataFrame(data,columns=['Main File','Dependency Files','Main_File_Path','Dependency_File_Paths'])
        st.markdown(f"**Summary**")
        dep_df.to_csv(cwd.rstrip('/')+'/discovery_refactor_files_output.csv',index=False)
        st.dataframe(dep_df[['Main File','Dependency Files']],hide_index=True,height=300,width=720)
        st.session_state.clear()
        st.cache_data.clear()

if __name__ == '__main__':
    if runtime.exists():
        print("Running ......")
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())