from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException
import os

#from dotenv import load_dotenv

#load_dotenv()

#get your discovery api key and discovey url from the watson discovery reservation

#a
# discovery_apikey = ""
# url_discovery=""
# collection_name=""
# pdf_file_path=""
# #for engish it is "en-us"
# collection_language=""


discovery_apikey = os.environ["discovery_apikey"]
url_discovery=os.environ["url_discovery"]
project_name=os.environ["project_name"]
collection_name=os.environ["collectiom_name"]
pdf_file_path=os.environ["pdf_file_path"]
#for engish it is "en-us"
collection_language=os.environ["collection_language"]


# authentication
authenticator = IAMAuthenticator(discovery_apikey)
watson_discovery = DiscoveryV2( version= "2023-03-31", authenticator=authenticator)
watson_discovery.set_service_url(url_discovery)


#Creating a new project
def set_new_project (project_name):
    try:
         project_creation_result = watson_discovery.create_project(name=project_name, type="document_retrieval").get_result()
         project_id_discovery = project_creation_result["project_id"]
         print("Discovery project ID:\n" + project_id_discovery )
    except ApiException as e:
          if "Project with name" in str(e) and "already exists" in str(e):
             print("This project already exists. ")
             project_id_list = watson_discovery.list_projects().get_result()['projects']
             for project in project_id_list:
                    if (project_name == project['name']):
                        project_id_discovery = project['project_id']

    return project_id_discovery


#Getting project id for the project created
#To communicate with watson discovery , such as uploading docs and perfoeming 
#searched , project id is required
project_id = set_new_project (project_name)
print (project_id)

#create a collection
def create_new_collection (project_id,collection_name,  collection_language):
    setting_new_collection = watson_discovery.create_collection(project_id=project_id, name=collection_name, language=collection_language).get_result()
    return setting_new_collection

collection_discovery = create_new_collection (project_id, collection_name, collection_language="en-us")

print (collection_discovery)



#listing all the collections available in a project
collection_list = watson_discovery.list_collections(project_id=project_id).get_result()["collections"]
print (collection_list)

#get the collection_id based on collection name
def collection_id_by_name(collection_name, collection_list ):
    for collection in collection_list:
        if(collection_name==collection['name'].lower()):
            return collection['collection_id']

collection_id_discovery = collection_id_by_name(collection_name=collection_name, collection_list=collection_list)
print (collection_id_by_name(collection_name=collection_name, collection_list=collection_list))

#Watson Discovery — Adding documents through API

def upload_document (file_path):
    with open(file_path, "rb") as file:
        add_doc_response = watson_discovery.add_document(
             project_id=project_id,
             collection_id=collection_id_discovery, file=file, file_content_type='application/pdf').get_result()
        print (add_doc_response)
        # Getting the ID of the newly added document
        new_document_id = add_doc_response.get("document_id", None)
        
        if new_document_id:
            print(f"Newly added document ID: {new_document_id}")
        else:
            print("Error getting document ID.")
            

            
file_path = pdf_file_path
upload_doc_discovery = upload_document(file_path)
document_status = watson_discovery.list_documents(collection_id=collection_id_discovery, project_id=project_id)
#checking document status 
print (document_status)

#searching the content in watson discovery documents
#this is esample query .based on pdfs/ documents change the query
query="What is strong and Weak AI?"

def discovery_query(query, counter=1):
    query_results = watson_discovery.query(
        project_id=project_id, 
        collection_ids=[collection_id_discovery], 
        natural_language_query=query,
        count=counter).get_result()
    
    return query_results

query_results_discovery = discovery_query(query)


#returns most relevant
def filter_results(query_results_discovery):
    query_final_results = query_results_discovery["results"][0]['document_passages'][0]["passage_text"]
    return query_final_results

results_from_discovery = filter_results(query_results_discovery)
print (results_from_discovery)