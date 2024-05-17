from selenium_to_json_conversion import selenium_to_json_prev, save_multi_json
import pandas as pd
import streamlit as st
import sys
from streamlit.web import cli as stcli
from streamlit import runtime
import os

cwd = os.getcwd()
# ibm_cloud_url = sys.argv[1]
# watson_ai_project_id = sys.argv[2]
# watson_ai_api_key = sys.argv[3]
st.title("Selenium to JSON Conversion")

if runtime.exists():
    with st.spinner("Uploading files..."):
        with st.form("my-form", clear_on_submit=True):
            selenium_obj_files = st.file_uploader("Upload Your Selenium Object Files:", accept_multiple_files=True)
            selenium_test_files = st.file_uploader("Upload Your Selenium Test Files:", accept_multiple_files=True)
            submitted = st.form_submit_button("UPLOAD")

    if selenium_obj_files or selenium_test_files:
        with st.spinner("Converting to JSON..."):
            if not 'json_object_dict' in st.session_state:
                st.session_state.json_object_dict, st.session_state.testcase_final_dict = selenium_to_json_prev(selenium_obj_files,selenium_test_files)
                st.success("Files uploaded and converted successfully!")
            #st.session_state.json_object_dict = json_object_dict
            st.text("") # Empty space for separation

    st.write("Download Options:")
    custom_output_path = st.text_input("Enter output path:", "/Users/pinkal/Documents/projects/selenium_to_qualitia/code/output")

    if st.button("Download"):
        if custom_output_path.strip() != "":
            obj_df,tc_df = save_multi_json(st.session_state.json_object_dict,st.session_state.testcase_final_dict, custom_output_path)
            st.success("Output has been downloaded to {}".format(custom_output_path))
            st.markdown(f"**Testcase JSON**")
            st.dataframe(tc_df,hide_index=True)
            st.markdown(f"**Object JSON**")
            st.dataframe(obj_df,hide_index=True)
            st.session_state.clear()
            st.cache_data.clear()
        else:
            st.error("Please enter a valid output path.")

if __name__ == '__main__':
    if runtime.exists():
        print("Running ......")
    else:
        ibm_cloud_url = sys.argv[1]
        watson_ai_project_id = sys.argv[2]
        watson_ai_api_key = sys.argv[3]

        #make file
        filename = ".env"
        with open(filename, "w") as file:
            file.write(f"IBM_CLOUD_URL={ibm_cloud_url}\n")
            file.write(f"PROJECT_ID={watson_ai_project_id}\n")
            file.write(f"API_KEY={watson_ai_api_key}\n")

        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())