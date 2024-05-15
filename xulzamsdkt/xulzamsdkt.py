from pdfminer.high_level import extract_text
from genai import Client, Credentials
from genai.extensions.langchain import LangChainInterface
from genai.schema import (
    DecodingMethod,
    ModerationHAP,
    ModerationParameters,
    TextGenerationParameters,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
import concurrent.futures
from dotenv import load_dotenv
load_dotenv()

# if you are using standard ENV variable names (GENAI_KEY / GENAI_API)
credentials = Credentials.from_env()
        
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
   llm = LangChainInterface(
        model_id="mistralai/mixtral-8x7b-instruct-v01",
        client=Client(credentials=Credentials.from_env()),
        parameters=TextGenerationParameters(
            decoding_method='greedy',
            min_new_tokens=1,
            max_new_tokens=1500,
            random_seed=42,
            temperature=0.10,
            repetition_penalty=1.20,
            top_k=50,
            top_p=0.85,
            truncate_input_tokens=40000)
    )
   template = f"""
        <<SYS>>
            You are an expert in interprofessional relations in healthcare.
        <</SYS>>
        Context = ```{text_chunk}```
        <<INST>>
        Briefly look at given context to identify the key insights within the text.
        Look for:
        • the research question or reason for the text
        • the findings (Results, including tables and figures)
        • how the findings were interpreted (Discussion) 
        Refrain from using any other knowlege other then the reference material.
        Please don't share false information.
        And now write the note of you findings

        <</INST>>

        """
   summary = llm(template) 
   return summary

def make_prompt(text):
    prompt =  f"""
    context = ```{text}```
    <<SYS>>
        You are a team coaching expert working with an interprofessional team that includes physicians, social workers, occupational therapists, psychologists, and nurses.
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
    llm = LangChainInterface(
        model_id="mistralai/mixtral-8x7b-instruct-v01",
        client=Client(credentials=Credentials.from_env()),
        parameters=TextGenerationParameters(
            decoding_method='sample',
            min_new_tokens=1,
            max_new_tokens=3500,
            random_seed=42,
            temperature=0.10,
            repetition_penalty=1.20,
            top_k=50,
            top_p=0.85,
            truncate_input_tokens=40000 
        
        )
    )

    chunks = split_documents(doc_content, 15000, 1000)
    chunk_dict_with_index = {index: value for index, value in enumerate(chunks)}
    print(f"chunking done - {len(chunks)} chunks" )
    if len(chunks) == 1:
        prompt = make_prompt(chunks[0].page_content)
        final_summary = llm(prompt) 
        return final_summary
        
    else:
        combined_summary = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            combined_summary = list(executor.map(generate_summary, chunk_dict_with_index.keys()))[0]
        print("combined summary generated")
        prompt = make_prompt(combined_summary)
        final_summary = llm(prompt) 
        return final_summary

if __name__ == "__main__":
    pdf_path = 'file.pdf'
    documents = extract_text(pdf_path)
    final_summary = get_doc_summary(documents)
    print(final_summary)

