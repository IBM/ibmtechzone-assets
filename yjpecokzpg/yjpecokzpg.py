# pip install streamlit;pip install pypdf;pip install ibm_watson_machine_learning
import streamlit as st
from pypdf import PdfReader
from ibm_watson_machine_learning.foundation_models import Model
import sys
from streamlit.web import cli as stcli
from streamlit import runtime

ibm_cloud_url = sys.argv[1]
watson_ai_project_id = sys.argv[2]
watson_ai_api_key = sys.argv[3]

print(ibm_cloud_url,watson_ai_project_id,watson_ai_api_key)

def extract_paragraphs(uploaded_file):
    pdf_page=PdfReader(uploaded_file)
    text=""
    for page in pdf_page.pages:
        text+=page.extract_text()
    return text

def watsonx_call(prompt,characters,model_id,stop_sequences):
        model_id = model_id
        parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": characters,
        "repetition_penalty": 1,
        "stop_sequences": stop_sequences,
        "min_new_tokens": 0,
        }
        
        model = Model(
        model_id = model_id,
        params = parameters,
        credentials = {
            "url" : ibm_cloud_url,
            "apikey" : watson_ai_api_key
        },
        project_id = watson_ai_project_id,
        )
        print("Submitting generation request...")
        print("Prompt: ",prompt)
        generated_response = model.generate_text(prompt=prompt)
        return generated_response

def summary(text):
     prompt = f'''Summarize the provided passage comprehensively, ensuring every detail, key point, and significant aspect is captured succinctly. Give summary in concise bulleted points.
input_document : {text}
Summary :'''
     response=watsonx_call(prompt,1000,'ibm-mistralai/mixtral-8x7b-instruct-v01-q',[])
     return response

st.title("PDF Summarization")
entity1_file = st.file_uploader("Upload Your Pdf here ", type=['pdf'])
if entity1_file is not None:
  filename1 = entity1_file.name.split()[0].strip(".pdf")
summary_placeholder = st.empty()
pros_placeholder = st.empty()
cons_placeholder = st.empty()
if entity1_file is not None:
    data_1 = extract_paragraphs(entity1_file)

    summary_placeholder.subheader("Document Summaries")
    st.write(f"{filename1} Summary: \n\n", summary(data_1))

if __name__ == '__main__':
    if runtime.exists():
        print("Running ......")
    else:
        ibm_cloud_url = sys.argv[1]
        watson_ai_project_id = sys.argv[2]
        watson_ai_api_key = sys.argv[3]
        sys.argv = ["streamlit", "run", sys.argv[0],ibm_cloud_url,watson_ai_project_id,watson_ai_api_key]
        sys.exit(stcli.main())