import os
import pandas as pd
import streamlit as st
from streamlit import session_state
import xml.etree.ElementTree as ET
from base_functions import list_transformation_names, get_elements_by_attribute_value, \
    get_mapping_tag_names, extract_text_between_backticks, generate_access_token, get_sql_query, \
        get_unique_from_instances_by_to_instance, collect_transformations_and_connectors, read_mapping_xls, \
        get_sql_query_for_inst, get_inst_for_query_gen
from modelcall import get_result
from dotenv import load_dotenv
load_dotenv()
# Function to handle XML file parsing and transformation
import streamlit as st


class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def process_xml_file(xml_file_path):

    mapping_names = get_mapping_tag_names(xml_file_path)
    selected_mapping_name = st.selectbox("Select Mapping", mapping_names)

    # Get transformation names
    transformation_names = list_transformation_names(xml_file_path, selected_mapping_name)
    
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
        # matching_elements = get_elements_by_attribute_value(xml_file_path, selected_transformation)
        # matching_elements = get_unique_from_instances_by_to_instance(xml_file_path, selected_mapping_name, selected_transformation)
        # if len(matching_elements) >0:
        #     to_instance_name = next(iter(matching_elements))
        #     from_instance_names = matching_elements[to_instance_name]

        # # Extract text content from XML elements
        # transformations, connectors = collect_transformations_and_connectors(xml_file_path, to_instance_name, from_instance_names)

        # matching_texts = "".join((transformations+connectors))
        # Display matching elements in a scrollable window
        xls_file = "llm_inputs_for_ui 2.xls"
        xml_content,inst1,inst2 = read_mapping_xls(selected_transformation, xls_file)
        # inst2 = inst2+"Generate sql query only"
        matching_texts = xml_content

        st.text_area("Matching Elements", matching_texts, height=200)
        # st.text_area("prompt1", xml_content + inst1, height=500)
        

        # st.markdown(
        #             f'<style>.scrollable-code .st-cm {{ max-height: 300px; overflow-y: scroll; }}</style>',
        #             unsafe_allow_html=True
        #         )
        # st.code(txt_matching_texts, language='xml')
        
        # Button to generate SQL query
        if not st.session_state.generate_sql_clicked:
            if st.button("Generate SQL Query"):
                # Send prompt to WatsonXAI and display response
                iam_access_token = generate_access_token(os.environ["API_KEY"], os.environ["IAM_URL"])

                # response = get_sql_query(matching_texts, os.environ["ENDPOINT_URL1"), iam_access_token)
                # response1 = get_inst_for_query_gen(matching_texts, inst1, os.environ["ENDPOINT_URL1"), iam_access_token)
                response1 = get_result(inst1 +''' \n Write the text that describes the transformation happening from source to destination using information in connection list to do the transformation.
    The generated text should give source name, destination name, and transformation applied on each columns.
    Mention the appropriate transformation on columns using information available in destination. \n'''+" " + matching_texts)
                # instructions = response1.json()['results'][0]['generated_text']
                instructions = "Fetch "+response1.split("Fetch")[-1]
                
                # st.text_area("prompt2", inst2 + instructions, height=500)
                # st.write("Instructions for SQL Query Generation \n __________________________________________")
                # st.write(response1)
                response = get_sql_query_for_inst(instructions, inst2, os.environ["ENDPOINT_URL2"], iam_access_token)
                response = response.json()['results'][0]['generated_text']
                # response1 = extract_text_between_backticks(response)
                st.write("SQL Query Generated \n __________________________________________")
                st.write(response)
                # st.code(response1, language='sql')
                # st.session_state.generate_sql_clicked = True


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
