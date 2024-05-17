from flask import Flask
import os, getpass
import re
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv


app = Flask(__name__)

# set up root route
@app.route("/")
def watson_ce_root():
	return "You have reached Watson CE Platform root"

@app.route("/build_vectordb")
def build_vector_db():
	ragObj = ragChroma()
	(db, docs, quest) = ragObj.add_to_collection()


@app.route("/query_docs")
def query_docs():
	from ibm_cloud_sdk_core import IAMTokenManager

	from watson_CE_modules import watson_x
	from watson_CE_modules import watson_discovery
	from watson_CE_modules import watson_assistant

	mt_model = 'bigscience/mt0-xxl'
	flanul_model = 'google/flan-ul2'
	falcon = "tiiuae/falcon-40b"
	llama2 = "meta-llama/llama-2-70b-chat"
	t5 = "google/flan-t5-xxl"

	##############   WATSON ASSISTANT STARTS HERE ###################################
	'''
	wassist_url = "https://api.us-south.assistant.watson.cloud.ibm.com/instances/d5db9793-212c-4577-9ab9-f588103203ea"
	wassist_version = "2023-06-15"
	wassist_api_key = ""
	waObj = watson_assistant.WatsonAssitantCE(wassist_api_key, wassist_version, wassist_url)
	print ("WA created")
	# waObj.create_new_assistant("assistant_api_one")
	waObj.select_existing_assistant("federal_assist")
	waObj.send_to_assistant("Hi")
	'''
	
	##############   CHROMA DB STARTS HERE ###################################
	'''
	question_index = 65
	releventTexts = ragObj.get_relevent_chunks(db, quest, question_index)
	# ragObj.send_to_ai(releventTexts)
	'''


	##############   WATSON DISCOVERY STARTS HERE ###################################
	'''
	ibm_cloud_url = "https://us-south.ml.cloud.ibm.com"
	discovery_url = "https://api.us-south.discovery.watson.cloud.ibm.com/instances/41bc6a09-ef59-40dc-87da-a4d888b26a5b"
	api_key = "-"
	project_id = ""

	# Name: itz-watson-apps-mfxemn8r-discovery

	wdObj = watson_discovery.WatsonDiscoveryCE(api_key, ibm_cloud_url, discovery_url, project_id)
	print ("WD created")
	relevent_docs = wdObj.wd_query_collection("Deduction under section 80C")
	print ("WD queried")
	'''


	##############   WATSON X AI STARTS HERE ###################################
	'''
	ibm_cloud_url = "https://us-south.ml.cloud.ibm.com"
	project_id = ""
	api_key = ""


	wxObj = watson_x.WatsonXCE(api_key, \
		ibm_cloud_url, \
		project_id, \
		model_name=llama2, \
		decoding_method="greedy",\
		max_new_tokens=100,\
		min_new_tokens=30, \
		temperature=1.0, \
		repetition_penalty=2.0)

	print (wxObj.wx_get_credentials())
	print (wxObj.get_details())

	#Q1 Code - enter prompt and parameters in this cell
	review = """Needed a nice lamp for my bedroom, and this one had \
	additional storage and not too high of a price point. \
	Got it fast.  The string to our lamp broke during the \
	transit and the company happily sent over a new one. \
	Came within a few days as well. It was easy to put \
	together.  I had a missing part, so I contacted their \
	support and they very quickly got me the missing piece! \
	Lumina seems to me to be a great company that cares \
	about their customers and products!!"""

	prompt = f"""Find the sentiment of the following text: 
	{review}""" #Complete your prompt here 
	
	response = wxObj.wx_send_to_watsonxai(prompts=[prompt],
		max_new_tokens=3,\
		min_new_tokens=1, \
		temperature=1.0, \
		repetition_penalty=2.0)


	
	return "Extracted the Named Entities"
	'''

	

# Get the PORT from environment
port = "8080"
if __name__ == "__main__":
	app.run(host='0.0.0.0',port=int(port))
	# ner_discovery()

