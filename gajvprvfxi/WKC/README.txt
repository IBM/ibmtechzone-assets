README


Overview
This Python script retrieves asset information from Watson Knowledge Catalog (WKC). The assets are sourced from files stored in IBM Cloud Storage through established connections.

Steps to Set Up
1. Create a Bucket in IBM Cloud Storage and Upload Files
Log in to your IBM Cloud account.
Create a new bucket in IBM Cloud Storage.
Upload the files you want to access through Watson Knowledge Catalog (WKC) into this bucket.
2. Create a Catalog in WKC
Log in to your WKC account.
Create a new catalog in WKC.
3. Create a Connection in the Catalog
Inside the catalog, create a new connection that links WKC with your IBM Cloud Storage.
Add the necessary credentials from your IBM Cloud Storage during the connection creation process.
4. Access Connected Assets
After creating the connection, navigate to the connected assets section, choose the created connection and add the files to WKC.
The files from your cloud storage will be available in WKC for governance and monitoring.
5. Fetch Asset Details Using Code
The provided Python script helps you fetch asset details through WKC APIs.

Configuration
For running the code, ensure the following details are specified in config.py:

API_KEY
CATALOG_ID
TOKEN_URL
CONNECTION_ID
WKC_URL
WATSONX_URL
PROJECT_ID