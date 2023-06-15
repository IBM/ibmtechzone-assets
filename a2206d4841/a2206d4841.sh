#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <json_input>"
  exit 1
fi

json_input=$1

# Extract the value of 'n' from the JSON input
n=$(echo "$json_input" | jq -r '.n')

if [ -z "$n" ]; then
  echo "Invalid JSON input. 'n' is missing."
  exit 1
fi

for ((i=1; i<=n; i++)); do
  echo $i
done