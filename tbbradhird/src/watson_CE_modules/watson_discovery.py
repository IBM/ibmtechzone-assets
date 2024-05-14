import json
import os
from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import CloudPakForDataAuthenticator,IAMAuthenticator
import text_extensions_for_pandas as tp

'''
Pre-requisites: 
pip install --upgrade "ibm-watson>=7.0.0"
pip install text-extensions-for-pandas
'''


class WatsonDiscoveryCE(DiscoveryV2):
	def __init__(self, param_api_key, param_ibm_cloud_url, param_url, proj_id):
		self.api_key = param_api_key
		self.ibm_cloud_url = param_ibm_cloud_url
		self.discovery_url = param_url

		self.discovery_pj_id = ""
		self.discovery_coll_id = ""
		
		if self.api_key is None or self.ibm_cloud_url is None or self.discovery_url is None:
			raise Exception("Ensure the credentials are correct !")
		else:
			pass

		self.authenticator = IAMAuthenticator(self.api_key)


		super().__init__(version='2023-03-31',
						authenticator=self.authenticator)
		self.set_service_url(self.discovery_url)

	def wd_query_collection(self, query_string):

		respones = self.query( 
					project_id=self.discovery_pj_id,
					collection_ids = None,
					filter = None,
					query = query_string,
					natural_language_query = "query_text",
					aggregation = None,
					count = 2	,
					return_ = ["title","metadata.source.url"],
					offset = None,
					sort = None,
					highlight = None,
					spelling_suggestions= None,
					table_results = {"enabled": False},
					suggested_refinements = None,
					passages=  { "enabled": True, "find_answers":True, "fields":["text", "original_text"], 
				 				"characters":150, "find_answers":True, "per_document":True
								},
					similar = None
				)
		return respones
	
	def wd_create_project_collection(self,target_pj_name='proj_name',target_coll_name='coll_name'):
		pj_list_resp = self.list_projects()
		existing_pj_names = [x["name"] for x in pj_list_resp.result["projects"]]
		if target_pj_name not in existing_pj_names:
			try:
				respPJ = self.create_project(name=target_pj_name, type="document_retrieval")
				if(respPJ.status_code == 201):
					self.discovery_pj_id = respPJ.result["project_id"]
					print ("Created Project with name ", target_pj_name, " under the id:", self.discovery_pj_id )
					try:
						#Create Discovery Collection
						respColl = self.create_collection(project_id=self.discovery_pj_id, name=target_coll_name)
						if(respColl.status_code == 201):
							self.discovery_coll_id = respColl.result["collection_id"]
							print ("Created Collection with name ", target_coll_name, " under the id:", self.discovery_coll_id )
						else:
							print ("Discovery Collection response code:", respColl.status_code)
					except:
						print ("Exception Creating Discovery Collection")

					else:
						print ("Collection ", target_coll_name, "already present in Cloud. Retrieving collection id ")
							
				else:
					print ("Discovery Project response code:", respPJ.status_code)
			except:
				print ("Exception creating Discovery Project")
			

		else:
			#Retrieve project id & collection id from existing cloud
			print ("Project ", target_pj_name, "already present in Cloud. Retrieving project ID")
			for elem in pj_list_resp.result["projects"]:
				if(elem["name"] == target_pj_name):
					self.discovery_pj_id = elem["project_id"]

			coll_list_resp = self.list_collections(self.discovery_pj_id)
			for elem in coll_list_resp.result["collections"]:
				if(elem["name"] == target_coll_name):
					self.discovery_coll_id = elem["collection_id"]


	def wd_extract_table_data(self,response):
		#TODO: Create enrichments and set the mode as pretrained model for SDU via code
		'''
		Generic method to extract the tabular data identified by discovery. Needs to be modified accordingly as per the usecase
		args: response - response from the discovery in JSON format
		returns: pandas dataframe with the tabular data; which further can be sent in the prompt to LLM
		'''
		key = "enriched_html"
		tables = [table for result in response['results'] 
					if key in result for enriched_html in result ['enriched_html']
					for table in enriched_html['tables']]
		table_data = tp.io.watson.tables.parse_response({"tables":tables})
		table_df = tp.io.watson.tables.make_table(table_data)

		return table_df

	def wd_add_document_to_discovery(self,fileName):
		with open(os.path.join(os.getcwd(), fileName),'rb') as fileinfo:
			response = self.add_document(
				project_id=self.discovery_pj_id,
				collection_id=self.discovery_coll_id,
				file=fileinfo,
				filename=fileName,
				file_content_type='application/pdf'
			)
			return response	