import os
import json
from tqdm import tqdm
from io import BytesIO, StringIO
from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv
load_dotenv()

WD_API_KEY = os.getenv('wd_api_key')
WD_API_URL = os.getenv('wd_api_url')
WD_PROJECT_ID = os.getenv('wd_project_id')

class DiscoveryClient:
    def __init__(self):
        authenticator = IAMAuthenticator(WD_API_KEY)
        self._discovery = DiscoveryV2(
            version='2023-03-31',
            authenticator=authenticator
        )

        self._discovery.set_service_url(WD_API_URL)
        self._discovery.set_disable_ssl_verification(True)

    def create_new_collection(self, collection_name, project_id=WD_PROJECT_ID, collection_language = 'en-us'):
        response = self._discovery.create_collection(project_id=project_id, name=collection_name, language=collection_language).get_result()
        return response
    
    def upload_pdf_document(self, file: str | BytesIO, 
                            collection_id: str,
                            project_id: str=WD_PROJECT_ID,
                            filename: str=""):
        """
        Uploads a PDF document to the specified collection and project.

        Args:
            file (Union[str, BytesIO]): The file to upload, either as a path (str) or an in-memory BytesIO object.
            collection_id (str): The ID of the collection to upload the document to.
            project_id (str, optional): The ID of the project. Defaults to WD_PROJECT_ID.
            filename (str, optional): The filename for the document. Required if 'file' is a BytesIO object.

        Raises:
            FileNotFoundError: If the file path does not exist.
            TypeError: If the 'file' parameter is neither a str nor a BytesIO object.
            ValueError: If 'file' is a BytesIO object and 'filename' is not provided.
        """
        if isinstance(file, str):
            if not filename:
                _, filename = os.path.split(file)
            file = open(file, "rb")
        elif isinstance(file, BytesIO):
            if not filename:
                raise ValueError("A filename must be provided when the file is a BytesIO object.")
            file.seek(0)
        else:
            raise TypeError("The 'file' parameter must be either a file path (str) or a BytesIO object.")
        
        add_doc_response = self._discovery.add_document(
            project_id=project_id,
            collection_id=collection_id, 
            file=file,
            filename=filename,
            file_content_type='application/pdf').get_result()
        new_document_id = add_doc_response.get("document_id", None)
        return new_document_id
        
    def get_all_chunks(self, collection_id, filename="", project_id=WD_PROJECT_ID, count=1000):
        if filename:
            filter = f'extracted_metadata.filename:"{filename}"'
        else:
            filter = None
        query_results = self._discovery.query(
            project_id=project_id,
            collection_ids=[collection_id],
            filter=filter,
            count=count  
        ).get_result()
        return query_results
    
    def copy_chunks_to_collection(self, from_collection_id, to_collection_id, project_id=WD_PROJECT_ID):
        query_results = self.get_all_chunks(collection_id=from_collection_id)
        for result in tqdm(query_results["results"]):
            document_id = result["document_id"]
            filename = result["extracted_metadata"]["filename"]
            copy_file = StringIO()
            copy_file.write(json.dumps(result, indent=4))
            copy_file.seek(0)
            add_doc = self._discovery.update_document(project_id=project_id, 
                                                      collection_id=to_collection_id, 
                                                      document_id=document_id, 
                                                      file=copy_file,
                                                      file_content_type="application/json",
                                                      filename=filename).get_result()

    def delete_all_docs_in_collection(self, collection_id, project_id=WD_PROJECT_ID):
        docs = self._discovery.list_documents(
                project_id=project_id,
                collection_id=collection_id,
                is_parent=False
            ).get_result()
        
        for doc in tqdm(docs['documents']):
            doc_id = doc["document_id"]
            response = self._discovery.delete_document(
                project_id=project_id,
                collection_id=collection_id,
                document_id=doc_id
            ).get_result()

    def list_all_collections(self, project_id=WD_PROJECT_ID):
        collections = self._discovery.list_collections(project_id=project_id).get_result()
        return collections
    
    def get_all_parent_filenames(self, collection_id, project_id=WD_PROJECT_ID):
        docs = self._discovery.list_documents(
            project_id=project_id,
            collection_id=collection_id,
            is_parent=True
        ).get_result()

        filenames = []
        for doc in docs['documents']:
            doc_details = self._discovery.get_document(project_id=project_id,
                                                collection_id=collection_id,
                                                document_id=doc['document_id']).get_result()
            filenames.append(doc_details['filename'])
        return filenames
    
    def check_document_status(self, document_id: str, collection_id: str, project_id: str=WD_PROJECT_ID):
        doc_details = self._discovery.get_document(project_id=project_id,
                                                   collection_id=collection_id,
                                                   document_id=document_id).get_result()
        status = doc_details['status']
        if status == 'processing':
            child = doc_details['children']['count']
            if child>0:
                try:
                    doc_details_0 = self._discovery.get_document(project_id=project_id,
                                                    collection_id=collection_id,
                                                    document_id=document_id + "_0").get_result()
                    doc_details_last = self._discovery.get_document(project_id=project_id,
                                                    collection_id=collection_id,
                                                    document_id=f"{document_id}_{child-1}").get_result()
                    if doc_details_0['status'] == doc_details_last['status']:
                        status = doc_details_0['status']
                except:
                    pass
        return status
