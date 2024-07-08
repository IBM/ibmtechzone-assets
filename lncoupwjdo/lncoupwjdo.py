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

def watsonx_call(prompt,model_id):
        model_id = model_id
        parameters = {
        'temperature' : .2,
    'min_new_tokens': 1,
    'max_new_tokens': 4095,
    'repetition_penalty': 1.12,
    'random_seed' : 10,
    'decoding_method': "sample"
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
     prompt = f"""<|system|>
        You are a person writing summaries of meeting transcripts at a corporate bank with clients. Write important key-points discussed in the meeting. Focus on telling who is State Street team offering information on products and who else is client, showing reactions on the product.
        Please focus on information shared by the client and the client's reaction to your product offering while generating summary.
        Include the following key points discussed during the meeting: [agenda items, discussion points, decisions made, action items assigned to specific individuals, attachments or documents shared].
        Which decision made in this call is very important, so don't leave it out.
        Ensure accuracy and clarity in the notes to facilitate seamless follow-up and reference for all attendees and stakeholders.
        <|user|>
            - If there is nothing important, don't output anything.
            - Generate summary from the input in bullet points.
            - Focus on client details while generating summary.
            - Focus on what the client talks about in the meeting.
            - Include information about the client's business and any challenges the client faces.
            - Do not repeat dialogue from the meeting.
            - Do not make assumption and make up any information. 
        <|user|>





\n \n 
input_document : {text}\n \n
OUTPUT: \n<|assistant|>"""
     response=watsonx_call(prompt,'ibm/granite-13b-chat-v2')
     return response

st.title("Transcript Summarization")
entity1_file = st.file_uploader("Upload Your transcript here ", type=['pdf'])
if entity1_file is not None:
  filename1 = entity1_file.name.split()[0].strip(".pdf")
summary_placeholder = st.empty()
pros_placeholder = st.empty()
cons_placeholder = st.empty()
if entity1_file is not None:
    data_1 = extract_paragraphs(entity1_file)

    summary_placeholder.subheader("Summary")
    st.write(summary(data_1))

if __name__ == '__main__':
    if runtime.exists():
        print("Running ......")
    else:
        ibm_cloud_url = sys.argv[1]
        watson_ai_project_id = sys.argv[2]
        watson_ai_api_key = sys.argv[3]
        sys.argv = ["streamlit", "run", sys.argv[0],ibm_cloud_url,watson_ai_project_id,watson_ai_api_key]
        sys.exit(stcli.main())
