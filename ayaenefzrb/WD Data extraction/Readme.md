
Description:
Asset facilitates metadata addition during data ingestion in Watson Discovery, as well as extraction of the full document using Watson Discovery.

Instructions for Use:
Ensure the .env file is located in the same directory, then execute the "Add_metadata_and_extract_document.py" python file. Uncomment.

Explanation: 
Each comment explains functionality of corresponding content.
Function "ingest_documents" pertains to process of ingesting documents along with their metadata.
Main function focuses on creating project and collection using object to ingest document along with metadata.

Line 75 creates object by passing project id and collection id of project created previously. In line 77, text has been extracted from ingested documents.