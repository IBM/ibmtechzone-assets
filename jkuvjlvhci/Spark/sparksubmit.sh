#!/bin/bash

# Loop through the set numbers
for ((i=1; i<=4; i++))
do
    # Construct the JSON file name
    json_file="submit-spark-app_32_D19_SaveId_5_s2_medium_set${i}.json"
    
    
    # Submit the Spark application using curl
    curl https://api.eu-de.ae.cloud.ibm.com/v3/analytics_engines/29ac93d5-b8f8-40bc-9833-7234829dbd14/spark_applications \
         -H "Authorization: Bearer ${IBM_CLOUD_IAM_TOKEN}" \
         -H "content-type: application/json" \
         -d "@$json_file"
done

