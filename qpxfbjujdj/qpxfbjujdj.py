import json
from datetime import datetime

output_json = "/projects/allScripts/config.json"

def append_from_nupur():
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare the message in the desired format
    new_data = {"timestamp": timestamp, "message": "From Python"}
    
    # Read the existing JSON data
    with open(output_json, 'r') as json_file:
        existing_data = json.load(json_file)
    
    # Create a list containing the existing data
    existing_data_list = existing_data if isinstance(existing_data, list) else [existing_data]
    
    # Append the new message to the existing data list
    existing_data_list.append(new_data)
    
    # Write the modified data back to config.json
    with open(output_json, 'w') as json_file:
        json.dump(existing_data_list, json_file)

append_from_nupur()
