import json

def flatten_json(obj, parent_key='', sep='_'):
    items = []
    for key, value in obj.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_json(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)

def read_and_process_json(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    
    # Flatten the JSON data
    flat_data = flatten_json(data)
    
    # Extract keys and values for the _list entries
    keys_list = list(flat_data.keys())
    values_list = list(flat_data.values())

    # Add the _list entries to the flattened data
    flat_data['key_name_list'] = keys_list
    flat_data['value_name_list'] = values_list

    return flat_data

# Assuming your JSON file is named 'example.json'
file_path = 'example.json'
processed_json = read_and_process_json(file_path)

# To see the processed, flattened JSON
print(json.dumps(processed_json, indent=4))
