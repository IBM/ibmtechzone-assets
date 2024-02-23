#!/bin/bash

# Set the hardcoded file paths
output_log="/projects/allScripts/test.log"
output_json="/projects/allScripts/config.json"

# Check if correct number of arguments are provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <welcome_message>"
    exit 1
fi

# Extract the welcome message from the argument
welcome_message="$1"

# Get the current timestamp
timestamp=$(date +"%Y-%m-%d %T")

# Append the message to the log file
echo "[$timestamp] $welcome_message --from bash" >> "$output_log"

# Construct the JSON object
json_data="{\"message\": \"$welcome_message\"}"

# Write the JSON data to the specified file
echo "$json_data" > "$output_json"

# Display the welcome message
echo "Welcome Message: $welcome_message"

# Display a confirmation message
echo "Welcome message has been written to $output_log and $output_json"
