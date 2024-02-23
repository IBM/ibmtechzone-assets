#!/bin/bash

# Set the hardcoded file paths
output_log="/projects/allScripts/test.log"
input_json="/projects/allScripts/config.json"
# Get the current timestamp
timestamp=$(date +"%Y-%m-%d %T")
welcome_message="Hello World"
cd
wget https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz
tar -xvzf apache-maven-3.9.6-bin.tar.gz
export PATH=/home/user/apache-maven-3.9.6/bin:$PATH
mvn --version

# Append the message to the log file
echo "[$timestamp] $welcome_message --from bash" >> "$output_log"

# Display the welcome message
echo "Welcome Message: $welcome_message"

# Display a confirmation message
echo "Welcome message has been written to $output_log by Maven"