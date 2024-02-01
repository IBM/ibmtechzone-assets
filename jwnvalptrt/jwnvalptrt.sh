#!/bin/bash

# Set default CSV file path
default_csv_file="/projects/allScripts/sample.csv"

# Check if a CSV file is provided as an argument, otherwise use the default path
if [ $# -eq 0 ]; then
    echo "No CSV file path provided. Using the default path: $default_csv_file"
    csv_file="$default_csv_file"
else
    csv_file=$1
fi

# Check if the file exists
if [ ! -f "$csv_file" ]; then
    echo "Error: File $csv_file not found."
    exit 1
fi

# Display CSV header with proper alignment
awk -F, 'NR==1 {for (i=1; i<=NF; i++) printf "\033[1;34m%-20s\033[0m", $i; print ""}' "$csv_file"

# Display CSV content with proper alignment
awk -F, 'NR>1 {for (i=1; i<=NF; i++) printf "%-20s", $i; print ""}' "$csv_file"