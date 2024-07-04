Description:
This asset facilitates the addition of metadata during data ingestion in Watson Discovery, as well as the extraction of the full document using Watson Discovery.

Instructions for Use:
Ensure the .env file is located in the same directory, then execute the "Add_metadata_and_extract_document.py" Python file. Uncomment lines 77 and 78 once the documents are available in Discovery, and execute these lines to extract and print the full document.

Explanation:
Each comment explains the functionality of corresponding content. The function "ingest_documents" pertains to the process of ingesting documents along with their metadata. The main function focuses on creating a project and collection using an object to ingest documents along with metadata.

Line 75 creates an object by passing the project ID and collection ID of the project created previously. In line 77 and 78, text is extracted and printed from the ingested documents.