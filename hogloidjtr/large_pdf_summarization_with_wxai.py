# Author: Pinkal Patel

'''
Title: Large PDF (>100 MB) Summarization With Watsonx.AI
Description:
This Assest is summarization of large pdf using Watsonx.AI with controlled parallel call.

Library:
pip install ibm_watson_machine_learning==1.0.357;
pip install python-dotenv==1.0.0;
pip install langchain==0.2.1;
pip install ibm-watson==7.0.1;
'''
from pdfminer.high_level import extract_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from WatsonxAPI import WatsonxAPI
from config import watsonx_pdf_summarization_config
import concurrent.futures

# Handle parallel call for Watsonx.AI
parallel_req_call = 8

llm = WatsonxAPI(watsonx_pdf_summarization_config)
        
def split_documents(documents, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        # separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    splits = text_splitter.split_text(documents)
    doc = text_splitter.create_documents(splits)
    chunks = text_splitter.split_documents(doc)
    return chunks

def generate_summary(text_chunk):
   template = f"""
        <<SYS>>
            You are an expert to write a concise summary in any domain.
        <</SYS>>
        Context = ```{text_chunk}```
        <<INST>>
        Briefly look at given context to identify the key insights within the text.
        Please don't share false information.
        And now write the note of you findings

        <</INST>>

        """
   summary = llm._generate_text(prompt = template) 
   return summary

def make_prompt(text):
    prompt =  f"""
    context = ```{text}```
    <<SYS>>
        You are an expert to write a concise summary in any domain.
    <</SYS>>
    <<INST>>
         Write to an intelligent, interested, naive, and slightly lazy audience (e.g.yourself, your friends). Expect your readers to be interested, 
         but don't make them struggle to understand you. Include all the important details; don't assume that they are already understood.
    • Eliminate wordiness, including most adverbs ("very", "clearly"). "The results clearly showed that there was no difference between the groups” can be shortened to "There was no significant difference between the groups".
    • Use specific, concrete language. Use precise language and cite specific examples to support assertions. Avoid vague references (e.g. "this illustrates" should be "this result illustrates").
    • Use scientifically accurate language. For example, you cannot "prove" hypotheses (especially with just one study). You "support" or "fail to find support for" them.
    • Do not write out the author or title.
    • Don't say things like  "Sure!....." Be concise.
    • Re-read what you have written. 
    • Do not refer to yourself. Just clearly summarize the text.
    
    ***Follow the below given structure of the response summary:***
    
    Introduction: 
    <Short Introduction that refers to the text and covers broadly everything, don't refer to yourself. >/n
    Key points: 
    <Write out the important points in the text that will cover broadly everything, don't refer to yourself>/n
    <</INST>>
    """
    return prompt

    

def get_doc_summary(doc_content):
    chunks = split_documents(doc_content, 15000, 1000)
    #print("chunks: ",chunks[:2])
    #chunk_dict_with_index = {index: value for index, value in enumerate(chunks[:6])}
    print(f"chunking done - {len(chunks)} chunks" )
    if len(chunks) == 1:
        prompt = make_prompt(chunks[0].page_content)
        final_summary = llm._generate_text(prompt = prompt)
        return final_summary
        
    else:
        combined_summary = []
        for i in range(0,int(len(chunks)/parallel_req_call)+1):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                #combined_summary = list(executor.map(generate_summary, chunk_dict_with_index.keys()))[0]
                sub_summary = list(executor.map(generate_summary, chunks[i*parallel_req_call:(i*parallel_req_call)+parallel_req_call]))
            combined_summary +=sub_summary
        print("combined summary generated: \n", len(combined_summary))#, combined_summary)
        if "I am unable to analyze the provided context" in combined_summary[:200]:
            return "I am unable to analyze the provided context."
        prompt = make_prompt(combined_summary)
        final_summary = llm._generate_text(prompt = prompt)
        return final_summary

if __name__ == "__main__":
    pdf_path = 'PM-6911-April-2021.pdf'
    documents = extract_text(pdf_path)
    final_summary = get_doc_summary(documents)
    print("======> final_summary: \n",final_summary)

