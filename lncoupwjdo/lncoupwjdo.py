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
            - Don't use example output as output of this transcript.
            - Generate summary from the input in bullet points.
            - Use bank terms mentioned in the meeting. 
            - Focus on client details while generating summary.
            - Focus on what the client talks about in the meeting.
            - Include information about the client's business and any challenges the client faces.
            - Do not repeat dialogue from the meeting.
            - Do not make assumption and make up any information. 
        <|user|>



INPUT: 
Noah Hodge: State Street, global markets, foreign exchange sales, trading and research. And I was thinking if we could go around the Horn, and you know. introduce yourselves 
and hear more about your uses. Fx process season and whatnot. Jaime Del Rio: Yeah, yeah, that sounds great. I guess I'll kick us off. Hi, Noah. Pleasure to meet 
you. Thanks for for taking the time as well. Yeah. My name is Jaime. I am the CEO of Jdr. Asset management. Yeah. So we're an alternative investment manager here 
in New York. Got about 10 billion and asked under management. couple of focuses as far as we go macro as well as quant discretionary macro strategies. But before I get too far into 
the weeds I'll let my 2 associates introduce themselves. Sarah Bishop: Hi, Noah! Thank you for having us today. I'm really excited to hear about. But you're gonna say to us. I'm Sarah, 
and I'm the portfolio manager here at Jdr. Asset management, focusing on trading our emerging markets for an exchange. Sophia Theodore: Hey, Noah, thanks for taking the time. 
I'm Sophia. I'm the specialist focusing for foreign exchange. Sorry. Just a little bit chaotic on the desk right now. So cameras can stay off for the meeting.

OUTPUT: 
- Noah Hodge met with Jaime the CEO or JDR Asset Management, Sarah the portfolio manager at JDR Asset Management focusing on trading their emerging markets, and 
Sophia the specialist focusing on foreign exchange. 
- JDR Asset Management is an alternative investment manager in New York with about 10 billion in assets under management. 


INPUT:
Noah Hodge: Alright sweet. Thank you all. I think on my end. Would a high, level overview of State Street be helpful for you guys to start off. Jaime Del Rio: Yeah, yeah, we're. 
We're relatively familiar with you. But yeah, if you could just kind of give us the rundown that would definitely help get the gears turning. Noah Hodge: Yeah, absolutely. Well, 
yeah, just to start off like I said, my name is Noah. I sit on the Foreign Exchange sales, trading research arm of State Street. I sit on the direct effects desk 
where we trade on a principal basis with our counterparties, which something I can get into a little a little later on in the meeting, but for now quick overview of our business 
before we jump into specifics at State Street Fx. Businesses, you know, within our global markets division of the bank. In the most recent industry, wide survey. We actually came 
out number 4 overall globally for fx providers as a whole, as well as the number one provider for swaps globally, and the number one provider of foreign exchange to 
our real money clients, and so here, on the direct effects desk, we trade roughly around 1,200 counterparties, deal in over 50 currencies on a 24Â h day, 5 day a week, basis for 
both spots and forwards. 13 locations across the globe, 3 in the Americas, 3 in Europe and 7 in Asia, Pacific. We also just recently bought a bank down in Sao. Paulo. Brazil opened 
an office down there. Message really being, we wanna have onshore presence in these restricted markets to offer onshore rates and competitive ndf. Pricing for our 
clients.


OUTPUT:
- Noah provides an overview of their business. He works in Foreign Exchange Sales, on the trading research arm of State Street. He focuses on FX where trading
is done on a principal basis with counterparties.

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
