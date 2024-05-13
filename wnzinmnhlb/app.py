import os
import pandas as pd
import streamlit as st
from streamlit import session_state
import xml.etree.ElementTree as ET
from base_functions import list_transformation_names, get_elements_by_attribute_value, get_response, extract_text_between_backticks, generate_access_token, get_sql_query
from dotenv import load_dotenv
load_dotenv()
# Function to handle XML file parsing and transformation
import streamlit as st


class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def process_xml_file(xml_file_path):
    # Get transformation names
    transformation_names = list_transformation_names(xml_file_path)
    
    # Display transformation names as select options
    selected_transformation = st.selectbox("Select Transformation", transformation_names)
    
    # Initialize session state
    if 'submit_clicked' not in st.session_state:
        st.session_state.submit_clicked = False
        st.session_state.generate_sql_clicked = False
    
    # Button to submit
    if not st.session_state.submit_clicked:
        if st.button("Submit"):
            st.session_state.submit_clicked = True
            
    if st.session_state.submit_clicked:
        # Trigger get_elements_by_attribute_value with selected value
        matching_elements = get_elements_by_attribute_value(xml_file_path, selected_transformation)
        
        # Extract text content from XML elements
        matching_texts = [ET.tostring(element, encoding='unicode') for element in matching_elements]

        txt_matching_texts = "\n".join(matching_texts)
        # Display matching elements in a scrollable window
        st.text_area("Matching Elements", txt_matching_texts, height=200)
        # st.markdown(
        #             f'<style>.scrollable-code .st-cm {{ max-height: 300px; overflow-y: scroll; }}</style>',
        #             unsafe_allow_html=True
        #         )
        # st.code(txt_matching_texts, language='xml')
        
        # Button to generate SQL query
        if not st.session_state.generate_sql_clicked:
            if st.button("Generate SQL Query"):
                # Send prompt to WatsonXAI and display response
                iam_access_token = generate_access_token(os.getenv("API_KEY"), os.getenv("IAM_URL"))

                response = get_sql_query(txt_matching_texts, os.getenv("ENDPOINT_URL"), iam_access_token)
                response = response.json()['results'][0]['generated_text']
                # response = get_response(txt_matching_texts)
                response1 = extract_text_between_backticks(response)
                st.write("SQL Query Generated:")
                st.write(response)
                st.code(response1, language='sql')
                st.session_state.generate_sql_clicked = True


# Main Streamlit app
def main():
    st.title("XML to SQL Query Generator")
    
    # File upload
    uploaded_file = st.file_uploader("Upload XML File", type=["xml"])
    
    if uploaded_file is not None:
        # Save uploaded file to current working directory
        file_path = os.path.join(os.getcwd(), uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Display uploaded file name
        st.write(f"Uploaded XML file: {uploaded_file.name}")
        
        # Process XML file
        process_xml_file(file_path)
    
if __name__ == "__main__":
    main()
