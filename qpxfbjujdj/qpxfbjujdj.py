import json
from datetime import datetime

# Hardcoded file paths
output_log = "/projects/allScripts/test.log"
output_json = "/projects/allScripts/config.json"

# Read the JSON data from the file
with open(output_json, 'r') as json_file:
    json_data = json.load(json_file)

# Extract the message from JSON data
message = json_data['message']

# Append "From Python" to the existing message
new_message = message + " From Python"

# Get current timestamp
current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]

# Append the new message to the log file
with open(output_log, 'a') as log_file:
    log_file.write(f"[{current_timestamp}] {new_message}\n")

# Display a confirmation message
print("New message has been appended to", output_log)
