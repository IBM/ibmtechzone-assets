#!/bin/bash

if [ -z "$n" ]; then
  echo "Invalid JSON input. 'n' is missing."
  exit 1
fi

for ((i=1; i<=n; i++)); do
  echo $i
done
