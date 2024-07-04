### Import Libraries and loading credentials
import watson_discovery
import os
from dotenv import load_dotenv
load_dotenv()

disc_api_key = os.getenv("DISCOVERY_API", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
dis_url= os.getenv("DISCOVERY_URL", None)
disc_api_key


### Ingestion of documents and it's metadata
def ingest_documents(wdObj,folder_path, file_type_dict):
    # For uploading multiple files from a folder
    folder_path = folder_path

    # Ensure the folder path exists
    if os.path.exists(folder_path):
        # List all files in the folder
        files = os.listdir(folder_path)
        print(files)

        # Iterate through each file in the folder
        for file_name in files:
            if file_name.startswith('.'):
                continue
            else:
                filename_w_ext = os.path.basename(file_name)
                
                # Split the file name and extension
                name, extension = os.path.splitext(file_name)
                
                # Remove the dot from the extension
                extension = extension.lower().lstrip('.')
                file_type = file_type_dict.get(extension, "unknown")
                print("Extension: ", file_type)
                file_path = os.path.join(folder_path, file_name)
                metadata_dict = {
                    "filename": filename_w_ext,
                    "file_type": file_type,
                    "column": "column_name"
                }
                # Construct the full path to the file
                file_path = os.path.join(folder_path, file_name)
                print("File Path: ", file_path)

                wdObj.wd_add_document_to_discovery(file_path =file_path, metadata=metadata_dict)

    else:
        print(f"The folder path '{folder_path}' does not exist.")


def main():
    # Use when Project and collection is not created
    wdObj = watson_discovery.WatsonDiscoveryCE(param_api_key=disc_api_key,param_ibm_cloud_url=ibm_cloud_url,param_url=dis_url, proj_id="", coll_id="")

    #Project and Collection creation
    wdObj.wd_create_project_collection(target_pj_name= "project_name", target_coll_name= "collection_name")

    # To map the extension of the file to get the file type 
    file_type_dict = {"docx": "doc",
                "doc" : "doc",
                "pptx" : "ppt",
                "ppt" : "ppt",
                "pdf" : "pdf"
                }
    ingest_documents(wdObj=wdObj, folder_path='provide_folder_path', file_type_dict=file_type_dict)

main()


# Uncomment below lines to retreive the document once available in Watson Discovery
# Use when Project and collection is already created
# wdObj = watson_discovery.WatsonDiscoveryCE(param_api_key=disc_api_key,param_ibm_cloud_url=ibm_cloud_url,param_url=dis_url, proj_id="project_id", coll_id="collection_id")
  
# response = wdObj.get_documents()
# print(response)
