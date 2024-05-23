import json
from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import elements_to_json

def process_json_file(input_filename, data_type, TXT_PATH):
    # Read the JSON file
    with open(input_filename, 'r') as file:
        data = json.load(file)

    extracted_elements = []
    for entry in data:
     if entry["type"] == "Table":
        if entry["type"] ==  data_type: # "NarrativeText"
            extracted_elements.append(entry["metadata"]["text_as_html"]) #entry["metadata"]["text_as_html"] entry["text"]

    with open(TXT_PATH, 'w') as output_file:
        for element in extracted_elements:
            output_file.write(element + "\n\n")
    
    return True


def extract_table_data(filename, strategy, model_name, JSON_PATH):
    
    elements = partition_pdf(
            filename=filename, 
            strategy=strategy, 
            infer_table_structure=True, 
            model_name=model_name
            )
    elements_to_json(elements, filename=JSON_PATH)
    
    return True

