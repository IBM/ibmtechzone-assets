import os
import sys
from dotenv import load_dotenv

from typing import Literal, Optional, Any, List
import bs4

import pandas as pd
import numpy as np
import time

import json
import numpy as np
from numpy.linalg import norm

import uvicorn
from fastapi import FastAPI, Response, status, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware



from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate

from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from langchain.llms import WatsonxLLM


# from watson_ce_pipelines import chroma_db
from watson_CE_modules import watson_x
from watson_CE_modules import watson_discovery


##### chat
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
	ChatPromptTemplate,
	HumanMessagePromptTemplate,
	MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from lang_chain import vector_stores
from sentence_transformers import SentenceTransformer
from watson_CE_modules import watson_discovery

from utils import pdf_loader
from utils import text_splitter

embeddings_model = vector_stores.HuggingFaceEmbeddings(model_name ='all-MiniLM-L12-v2')
model_emb = SentenceTransformer('all-MiniLM-L12-v2')

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


recent_pdf_name = ""


load_dotenv()
api_key_env = os.getenv("WATSONX_APIKEY", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
wx_project_id = os.getenv("WX_PROJECT_ID", None)

discovery_url = os.getenv("DISCOVERY_URL", None)
disc_api_key = os.getenv("DISCOVERY_API_KEY", None)


full_pdf_with_metadata = None

def make_prompt(context, question_text):
	return (f"{context}\n\nPlease answer a question using this "
		  + f"text. "
		  + f"If the question is unanswerable, say \"unanswerable\"."
		  + f"Question: {question_text}?")

def generate_ai_summary(prompt, api_key, ibm_cloud_url, project_id):
		##############   WATSON X AI STARTS HERE ###################################			
		print ("api_key:", api_key)
		print ("ibm_cloud_url:", ibm_cloud_url)
		print ("project_id:", project_id)
		wxObj = watson_x.WatsonXCE(api_key, \
			ibm_cloud_url, \
			project_id)

		response = wxObj.wx_send_to_watsonxai(prompts=[prompt],
			model_name="meta-llama/llama-2-70b-chat", \
			decoding_method="greedy",\
			max_new_tokens=100,\
			min_new_tokens=10, \
			temperature=0)

		return response



def send_to_ai(contextIn, question_text, api_key, ibm_cloud_url, project_id):
		prompt = make_prompt(contextIn, question_text)

		##############   WATSON X AI STARTS HERE ###################################			
		wxObj = watson_x.WatsonXCE(api_key, \
			ibm_cloud_url, \
			project_id)

		response = wxObj.wx_send_to_watsonxai(prompts=[prompt],
			model_name="meta-llama/llama-2-70b-chat", \
			decoding_method="greedy",\
			max_new_tokens=100,\
			min_new_tokens=10, \
			temperature=0)

		return response



recent_pdf_name = ""
# set up root route
@app.get("/")
def watson_ce_root():
	return Response(content='Reached WCE Root', status_code=status.HTTP_200_OK)


def preProcessLlmOutput(raw_string):
	cleanedResponse = raw_string.replace("Human","")
	cleanedResponse = cleanedResponse.replace("Chatbot","")
	cleanedResponse = cleanedResponse.replace("AI:","")
	cleanedResponse = cleanedResponse.replace("\n","")
	cleanedResponse = cleanedResponse.strip()
	return cleanedResponse



######## RETRIEVER ############
#Create Discovery Project if not present already
wdObj = None
new_pj_name = "discovery_api_pj"
new_coll_name = "discovery_api_collection"
try:
	wdObj = watson_discovery.WatsonDiscoveryCE(disc_api_key, ibm_cloud_url, discovery_url, "")
	wdObj.wd_create_project_collection(target_pj_name=new_pj_name,\
								target_coll_name=new_coll_name)
except:
	print ("[Watson Discovery] Configuration failed !")
	exit(0)

	
######### MODEL ############
print ('\n')
print ("Watson X credentials \n",api_key_env)
print (ibm_cloud_url)
print (wx_project_id)

parameters = {
	GenParams.DECODING_METHOD: "greedy",
	GenParams.MAX_NEW_TOKENS: 480,
	GenParams.MIN_NEW_TOKENS: 1,
	GenParams.TEMPERATURE: 0,
	# GenParams.TOP_K: 50,
	# GenParams.TOP_P: 1,
	# GenParams.STOP_SEQUENCES: ['\nHuman',"Chatbot\n", "\nChatbot", '\n\n']
	GenParams.STOP_SEQUENCES: ['\n\n']
}

watsonx_llm = WatsonxLLM(
	model_id="meta-llama/llama-2-70b-chat",
	url=ibm_cloud_url,
	project_id=wx_project_id,
	params=parameters,
)

watson_answer_prompt_start = """\nAgent: Okay, I am awaiting your instructions
\n\n
User:Watson, here are your instructions:
1. You are provided several documents.
2. You should generate response only using the information available in the documents.
3. If you can't find an answer, say \"I don't know\".
4. Do not use any other knowledge.
5. Summarise the response in precise manner and also don’t ask the questions .
6. Close the conversation with no further questions like system generated User questions.
7. While answering consider Dialysis as Hospitalization treatment and answer accordingly by giving explanation from document.

"""
watson_answer_prompt_end = """
Use the above context to improve the accuracy of the results.


\n\n
Agent:I am ready to answer your questions from the document. I will not repeat
answers I have given.
\n\n
User:{human_input}.

\n\n
Agent:"""


######## PROMPT ############
prompt = ChatPromptTemplate.from_messages(
[
	SystemMessage(
		# content="You are a chatbot having a conversation with a human."
		content=watson_answer_prompt_start
	),  # The persistent system prompt
	MessagesPlaceholder(
		variable_name="chat_history"
	),  # Where the memory will be stored.
	HumanMessagePromptTemplate.from_template(
		watson_answer_prompt_end
	),  # Where the human input will injected
]
)

memory = ConversationBufferWindowMemory(memory_key="chat_history", k=2, return_messages=True)


##### CHAIN #########
chat_llm_chain = LLMChain(
	llm=watsonx_llm,
	prompt=prompt,
	verbose=True,
	memory=memory,
)



class Query(BaseModel):
	query: str

class ResponseCustom(BaseModel):
	rag_response: str
	dummy_one: str
	dummy_two : str

@app.post("/get_model_response", response_model=ResponseCustom)
async def get_model_response(query: Query):
# def get_model_response_etxt(query):
	user_query = str(query).split('=')[1]
	print ("\nUser query:", user_query)

	##### CONTEXT ID ########
	similarity_status = True

	
	if(similarity_status):
		#Retain memory
		pass
	else:
		#Reset Memory
		print("Memory reset!")
		memory.clear()
		
	
	##### INVOKING ##########
	
	#Retreiver call
	try:
		response_wd = wdObj.wd_query_collection(str(user_query))
	except:
		print ("Discovery query exception")
		sys.exit(0)

	context_text = ""
	if(response_wd.status_code == 200):
		resp_result = response_wd.get_result()
		for item in resp_result["results"]:
			context_text += str(item["document_passages"][0]["passage_text"])
		print ("\n Context:", str(context_text))
	else:
		print ("WD Exception")

	#Context update
	memory.save_context({"input": "Context"}, {"output": str(context_text.replace('[', '').replace(']', ''))})
	discovery_input = context_text
	inputs = {"human_input": user_query}

	##LLM call
	retval = chat_llm_chain.invoke(inputs)
	bot_response = preProcessLlmOutput(retval["text"])
	print ("\tHUMAN:", retval["human_input"])
	print ("\tBOT:", bot_response)
	
	return {"rag_response":str(bot_response), "dummy_one":"dummy_one", "dummy_two":"dummy_two"}
	

@app.post("/upload_file/")
async def create_upload_files(file: UploadFile = File(...)):
	contents = await file.read()
	global recent_pdf_name
	fileName = file.filename
	recent_pdf_name = fileName #Store For recent summarization feature
	print("fileName:",str(fileName))

	add_doc_resp = None

	with open(str(fileName.strip()), 'wb') as f:
		f.write(contents)
		time.sleep(1)

		try:
			add_doc_resp = wdObj.wd_add_document_to_discovery(fileName.strip())
		except:
			return Response(content="[Watson Discovery] Adding document failed !", status_code=status.HTTP_404_NOT_FOUND)
		
	time.sleep(5) #Time to reflect the file processing status in discovery
	if(add_doc_resp.status_code == 202):
		return Response(content='The document has been accepted and being processed', status_code=status.HTTP_200_OK)
	else:
		return Response(content="Error adding document to discovery", status_code=status.HTTP_404_NOT_FOUND)
			

@app.get('/check_discovery_progress')
def check_discovery_progress():
		under_processing_docs = 0
		collect_reponse = None
		try:
			collect_reponse = wdObj.get_collection(project_id=wdObj.discovery_pj_id, collection_id=wdObj.discovery_coll_id)
		except:
			return Response(content="Error in process", status_code=status.HTTP_404_NOT_FOUND)
			
		pending_docs = int(collect_reponse.result["source_document_counts"]["pending"])
		processing_docs = int(collect_reponse.result["source_document_counts"]["processing"])
		under_processing_docs = pending_docs + processing_docs
		# print ("under_processing_docs:", str(under_processing_docs))
		json_dump = json.dumps({"under_processing_docs":under_processing_docs})

		if (collect_reponse.status_code == 200):
			return Response(content=json_dump, status_code=status.HTTP_200_OK)
		else:
			return Response(content="Error in process", status_code=status.HTTP_404_NOT_FOUND)


class recentsummarizeResponse(BaseModel):
	raw_text_list : str
@app.post('/recent_summary/', response_model=recentsummarizeResponse)
def summarize_file():
	global recent_pdf_name
	global api_key_env
	global ibm_cloud_url
	global wx_project_id
	#Read file
	pdf_loader_obj = pdf_loader.pdfLoader()
	fileName = str(recent_pdf_name)
	print("\n\nRecent file for summarization:", str(fileName))
	raw_text_list, pdf_page_list, full_pdf_with_metadata = pdf_loader_obj.pdf_to_text('./'+str(fileName).strip())

	full_text = ""
	for elem in raw_text_list:
		full_text += str(elem)
	if(len(full_text) >= 3000):
		crop_text = full_text[0:3000]
	else:
		crop_text = full_text

	#Summarize
	llm_query = f"""Write a concise summary of the following:
	{crop_text}
	CONCISE SUMMARY:"""
	
	summary_resp = generate_ai_summary(llm_query, api_key_env, ibm_cloud_url, wx_project_id)

	rag_results = {"raw_text_list":summary_resp}
	print (str(rag_results))
	json_dump = json.dumps(rag_results)

	return Response(content=json_dump, status_code=status.HTTP_200_OK)

# Get the PORT from environment
# port = os.getenv('PORT', '8000')
server_port = 8000
if __name__ == "__main__":
	uvicorn.run( app, port=server_port)





