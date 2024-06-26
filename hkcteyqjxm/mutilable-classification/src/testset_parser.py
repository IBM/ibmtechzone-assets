from unstructured.partition.pdf import partition_pdf
from os import listdir
from unstructured.staging.base import elements_to_json
import ssl
import json

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

PARENT_FOLDER = r"../test_samples/"
JSON_RESULT_FOLDER = r"../test_preprocess/json"
TXT_RESULT_FOLDER = r"../test_preprocess/txt"

def file_reader(file_location, file):
    """
    file_reader will read the provided list of file in specified location and return text as outcome.
    """ 
    # Define parameters for Unstructured's library
    strategy = "hi_res" # Strategy for analyzing PDFs and extracting table structure
    model_name = "yolox" # Best model for table extraction. Other options are detectron2_onnx and chipper depending on file layout

    # Extracts the elements from the PDF
    elements = partition_pdf(
    filename=file_location, 
    strategy=strategy, 
    infer_table_structure=True, 
    model_name=model_name
    )

    json_location = ("//").join([JSON_RESULT_FOLDER,file.split(".pdf")[0]])
    print(json_location)
    # Store results in json
    elements_to_json(elements, filename=f"{json_location}.json")

    return True

def process_json_file(input_filename):
    # Read the JSON file
    json_file_location = ("//").join([JSON_RESULT_FOLDER,input_filename])
    txt_file_location = ("//").join([TXT_RESULT_FOLDER,input_filename.split(".json")[0]+".txt"])
    with open(json_file_location, 'r') as file:
        data = json.load(file)
    
    # Iterate over the JSON data and extract required table elements
    extracted_elements = []
    for entry in data:
        if entry["type"] == "Table":
            extracted_elements.append(entry["metadata"]["text_as_html"])
    
    # Write the extracted elements to the output file
    with open(txt_file_location, 'w') as output_file:
        for element in extracted_elements:
            output_file.write(element + "\n\n")


def PDF_to_text():
    """
    Identify each and every file present in the others folder and convert it into respective text file from PDFs.
    """  
    file_arr = listdir(PARENT_FOLDER)
    content_map = []
    for file in file_arr:
        print(file)
        content_map.append({"file_name":file,"file_content":file_reader(("//").join([PARENT_FOLDER,file]),file)})
    print(content_map)

def process_json():
    file_arr = listdir(JSON_RESULT_FOLDER)
    for file in file_arr:
        process_json_file(file)

process_json()