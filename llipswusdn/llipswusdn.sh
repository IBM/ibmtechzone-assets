#!/bin/bash

# Set the hardcoded file path
output_file="/projects/allScripts/test.log"

# Check if correct number of arguments are provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <welcome_message>"
    exit 1
fi

# Extract the welcome message from the argument
welcome_message="$1"

# Write the welcome message to the specified file
echo "$welcome_message" > "$output_file"

# Display a confirmation message
echo "Welcome message has been written to $output_file"
