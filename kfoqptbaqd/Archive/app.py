import streamlit as st
from csv_processor import process_csv, ProcessingError
from embedding_similarity import calculate_similarity

st.title('RAG Q&A Testing Application')

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

tab1, tab2 = st.tabs(["RAG with Watson Assistant", "Custom RAG"])

with tab1:
    # User inputs for Watson LLM credentials
    assistant_apikey = st.text_input("Enter your Watson Assistant API Key")
    assistant_url = st.text_input("Enter your Watson Assistant URL")
    draft_env_id = st.text_input("Enter your Watson Draft Environment ID")

    watsonai_apikey = st.text_input("Enter your Watsonx AI API Key for LLM", key='assistant_watsonai_apikey')
    ibm_cloud_url = st.text_input("Enter your IBM Cloud URL", key='assistant_ibm_cloud_url')
    project_id = st.text_input("Enter your Watsonx AI Project ID", key='assistant_project_id')

    print(ibm_cloud_url)



    # api_key = os.getenv("WATSONX_APIKEY", None)
    # ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
    # project_id = os.getenv("IBM_CLOUD_PROJECT", None)

    button_1 = st.button('Submit', key='assistant')
    with st.spinner("Fetching Watson Assistant's responses"):
        if button_1 and uploaded_file is not None and assistant_apikey and assistant_url and draft_env_id:
            try:
                processed_data = process_csv(uploaded_file, assistant_apikey, assistant_url, draft_env_id, watsonai_apikey, ibm_cloud_url, project_id)
                st.download_button(
                    label="Download data as CSV",
                    data=processed_data,
                    file_name='processed_data.csv',
                    mime='text/csv',
                )
            except ProcessingError as e:
                st.error(f"Error processing file: {e}")
with tab2:

    ip = st.text_input("Your Endpoint's IP", placeholder="Your Endpoint's IP", value='127.0.0.1')
    port = st.text_input("Your Endpoint's PORT", placeholder="Your Endpoint's PORT", value=5000)

    watsonai_apikey = st.text_input("Enter your Watsonx AI API Key for LLM", key='custom_watsonai_apikey')
    ibm_cloud_url = st.text_input("Enter your IBM Cloud URL", value='https://us-south.ml.cloud.ibm.com/', key='custom_ibm_cloud_url')
    project_id = st.text_input("Enter your Watsonx AI Project ID", key='custom_project_id')

    submit = st.button('Submit', key='custom')
    print(submit , uploaded_file , ip , port)
    if submit and ip and port and not uploaded_file:
        st.warning('Please upload the CSV file.')
    if submit and uploaded_file and ip and port:
        with st.spinner("Fetching custom RAG's responses"):
            print('running')
            try:
                processed_data =  process_csv(uploaded_file, watsonai_apikey=watsonai_apikey, ibm_cloud_url=ibm_cloud_url, project_id=project_id, ip=ip, port=port, rag_type = 'custom')
                st.download_button(
                    label="Download data as CSV",
                    data=processed_data,
                    file_name='processed_data.csv',
                    mime='text/csv',
                )
            except ProcessingError as e:
                st.error(f"Error processing file: {e}")
