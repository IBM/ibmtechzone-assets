from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import text_extensions_for_pandas as tp
from langchain.docstore.document import Document
import re, os, json

'''
Pre-requisites: 
pip install --upgrade "ibm-watson>=7.0.0"
pip install text-extensions-for-pandas
'''


class WatsonDiscoveryCE(DiscoveryV2):
    def __init__(self, param_api_key, param_ibm_cloud_url, param_url, proj_id, coll_id):
        self.api_key = param_api_key
        self.ibm_cloud_url = param_ibm_cloud_url
        self.discovery_url = param_url

        self.discovery_pj_id = proj_id
        self.discovery_coll_id = coll_id
        
        if self.api_key is None or self.ibm_cloud_url is None or self.discovery_url is None:
            raise Exception("Ensure the credentials are correct !")
        else:
            pass

        self.authenticator = IAMAuthenticator(self.api_key)


        super().__init__(version='2023-03-31',
                        authenticator=self.authenticator)
        self.set_service_url(self.discovery_url)


    # To query the collection
    def wd_query_collection(self, query_string):

        response = self.query( 
                    project_id=self.discovery_pj_id,
                    collection_ids = None,
                    filter = None,
                    query = query_string,
                    natural_language_query = "query_text",
                    aggregation = None,
                    count = 5,
                    return_ = ["result_metadata.confidence", "metadata", "document_passages"],
                    # return_ = ["result_metadata.confidence", "report", "lighthouse_id", "group"],
                    offset = None,
                    sort = None,
                    highlight = None,
                    spelling_suggestions= None,
                    table_results = {"enabled": False},
                    suggested_refinements = None,
                    passages=  { "enabled": True, "find_answers":True, "fields":["text", "original_text"], 
                                 "characters":300, "find_answers":True, "per_document":True, "max_per_document": 5
                                },
                    similar = None
                )
        return response
    
    # Extract the data from the ingested documents 
    def get_documents(self):
        """
        Retrieves documents from a project and collection using the Watson Discovery service.

        Returns:
            list: A list of Document objects containing the retrieved documents.
        """

        wd_client = DiscoveryV2(version="2020-08-30", authenticator=self.authenticator)
        wd_client.set_service_url(self.discovery_url)
        WD_PAGE_SIZE = 20
        results = [None]
        documents = []
        page_id = 0
        while len(results)!=0:
            response = wd_client.query(
                        project_id=self.discovery_pj_id,
                        collection_ids=[self.discovery_coll_id],
                        count=WD_PAGE_SIZE,
                        offset=page_id*WD_PAGE_SIZE
                    ).get_result()
            results = response['results']
            documents.extend(results)
            page_id +=1

        def pre_split_processing(txt):
            return re.sub(r'(\n[ \t]*)+', '\n\n', txt)

        documents = zip([pre_split_processing(d.get("text", [""])[0]) for d in documents],
                        [{"document_id":d["document_id"],
                        "parent_document_id": d['metadata'].get('parent_document_id', d["document_id"]),
                        "filename": d['extracted_metadata']['filename'],
                        "subtitle": d.get("subtitle", "")} for d in documents]
                    )
        documents = list(map(lambda x: Document(page_content=x[0], metadata=x[1]), documents))
        return documents

    # To create the Project and Collection inside it
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
                            # self.discovery_coll_id = respColl.result["collection_id", "smart_document_understanding": {"enabled": True, "model": "pre_trained"}]
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


    # Adding documents and it's metadata to collection
    def wd_add_document_to_discovery(self, file_path, metadata):
        # filename = metadata_dict["filename"]
        with open(os.path.join(os.getcwd(), file_path),'rb') as fileinfo:
            response = self.add_document(
                project_id=self.discovery_pj_id,
                collection_id=self.discovery_coll_id,
                file=fileinfo,
                filename=file_path,
                metadata=json.dumps(metadata),
                file_content_type='application/octet-stream'
            )
            return response	