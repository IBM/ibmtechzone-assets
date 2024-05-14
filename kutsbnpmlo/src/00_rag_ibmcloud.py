import os
#import fitz
import os
import re
import requests
import json
from typing import Literal, Optional, Any, List
import bs4

import uvicorn
from fastapi import FastAPI, Response, status, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


import pandas as pd
import numpy as np
import time
from dotenv import load_dotenv


# from watson_ce_pipelines import chroma_db
from watson_CE_modules import watson_x
from watson_CE_modules import watson_discovery

from utils import pdf_loader
from utils import text_splitter

import warnings
warnings.filterwarnings("ignore")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
api_key = os.getenv("WATSONX_APIKEY", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
project_id = os.getenv("WX_PROJECT_ID", None)



##############   WATSON DISCOVERY STARTS HERE ###################################
disc_ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
disc_discovery_url = os.getenv("DISCOVERY_URL", None)
disc_api_key = os.getenv("DISCOVERY_API_KEY", None)
# project_id = os.getenv("DISCOVERY_PROJECT_ID", None)



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



new_pj_name = "discovery_api_pj"
new_coll_name = "discovery_api_collection"

recent_pdf_name = ""

#Create Discovery Project if not present already
try:
	wdObj = watson_discovery.WatsonDiscoveryCE(disc_api_key, disc_ibm_cloud_url, disc_discovery_url, "")
	wdObj.wd_create_project_collection(target_pj_name=new_pj_name,\
								   target_coll_name=new_coll_name)
except:
	print ("[Watson Discovery] Configuration failed !")
	exit(0)


class recentsummarizeResponse(BaseModel):
	raw_text_list : str
@app.post('/recent_summary/', response_model=recentsummarizeResponse)
def summarize_file():
	global recent_pdf_name
	global api_key
	global ibm_cloud_url
	global project_id
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
	
	summary_resp = generate_ai_summary(llm_query, api_key, ibm_cloud_url, project_id)

	rag_results = {"raw_text_list":summary_resp}
	print (str(rag_results))
	json_dump = json.dumps(rag_results)

	return Response(content=json_dump, status_code=status.HTTP_200_OK)

	# return json_dump

class summarizeQuery(BaseModel):
	queryText: str

class summarizeResponse(BaseModel):
	raw_text_list : str

@app.post('/summarize_file', response_model=summarizeResponse)
async def summarize_file(queryText: summarizeQuery):
	global recent_pdf_name
	global api_key
	global ibm_cloud_url
	global project_id
	#Read file
	pdf_loader_obj = pdf_loader.pdfLoader()
	fileName = str(queryText.queryText)
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
	
	summary_resp = generate_ai_summary(llm_query, api_key, ibm_cloud_url, project_id)

	rag_results = {"raw_text_list":summary_resp}
	return rag_results

# set up root route
@app.get("/")
def watson_ce_root():
	return Response(content='Reached WCE Root', status_code=status.HTTP_200_OK)


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
	

class Query(BaseModel):
	query: str

class ResponseCustom(BaseModel):
	watsonx_response: str
	pageNums: str
	discovery_response : str


@app.post("/get_model_response", response_model=ResponseCustom)
async def get_model_response(query: Query):
	global api_key
	global ibm_cloud_url
	global project_id
	print ("\nUser query:", str(query))
	response_wd = None
	page_num = "0"
	resp_discvry = ""
	llmResp = "NULL"

	try:
		response_wd = wdObj.wd_query_collection(str(query))
	except:
		print ("Discovery query exception")
		llmResp = "Exception:"
		rag_results = {"watsonx_response":str(llmResp), "pageNums":str(page_num), "discovery_response":str(resp_discvry)}
		return rag_results

	if(response_wd.status_code == 200):
		resp_result = response_wd.get_result()
		context_text = ""
		for item in resp_result["results"]:
			context_text += str(item["document_passages"][0]["passage_text"])
			resp_discvry += context_text
		llmResp = str(send_to_ai(context_text, query, api_key, ibm_cloud_url, project_id))
		llmResp = llmResp.strip()
	else:
		llmResp = str(response_wd.status_code)

	rag_results = {"watsonx_response":str(llmResp), "pageNums":str(page_num), "discovery_response":str(resp_discvry)}
	return rag_results

@app.get("/query_docs")
async def query_docs(query: Optional[str] = None, \
					 model: Optional[str] = None, 
					 vectorDb: Optional[str] = None, 
					 embeddingModel: Optional[str] = None):
	response_wd = None

	print ("\n model:", model)
	print ("\n vectorDb:", vectorDb)
	print ("\n embeddingModel:", embeddingModel)
	print ("\n query:", query)


	try:
		response_wd = wdObj.wd_query_collection(query)
	except:
		return Response(content="Error in querying Watson Discovery", status_code=status.HTTP_404_NOT_FOUND)
	
	context_text = ""
	for item in response_wd["results"]:
		context_text += str(item["document_passages"][0]["passage_text"])

	llmResp = send_to_ai(context_text, query, api_key, ibm_cloud_url, project_id)
	json_dump = json.dumps({"watsonx_response":llmResp, "pageNums":['0'], "discovery_response":response_wd})
	if(llmResp): 
		return Response(content=json_dump, status_code=status.HTTP_200_OK)
	else:
		return Response(content="Error in process", status_code=status.HTTP_404_NOT_FOUND)
		

# Get the PORT from environment
# port = os.getenv('PORT', '8080')
port = str(8000)
if __name__ == "__main__":
	uvicorn.run(app)




'''
Better handling endpoint exception:

if:
	return Response(content=json_dump, status_code=status.HTTP_200_OK)
else: 
	raise HTTPException(status_code=400, detail="Text cannot be empty")

'''