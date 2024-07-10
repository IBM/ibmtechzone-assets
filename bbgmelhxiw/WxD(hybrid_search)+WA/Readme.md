Description:
This asset facilitates the integration of Watsonx Discovery with Watson Assistant to retrieve passages from multi-passage documents (keeping document structure intact) through a hybrid search query.

Instructions for Use:
Input a query related to documents ingested in Watsonx Discovery. The system will display the top 3 passages retrieved for that query. Setting "Verbose" to true shows the raw JSON response from Watsonx Discovery. Use the specified OpenAPI exclusively for creating the WxD extension due to additional parameters. The extracted entities array for this asset has been predetermined. You can retrieve entities using watsonx.ai based on your search query.

Explanation:
OpenAPI: Includes "min_score" to filter search results by minimum score.

Watsonx Discovery Search Action:
"query_body": Keyword search query body.
"raw_entities": Array of entities.
"ext_entity": Extracted entity from "raw_entities".
"query_body_nested": Part of query body for keyword matching, e.g., with product column.
"knn_body": Semantic matching using KNN.
"set_source": Set to avoid additional fields.
"set_min_score": Set minimum score for relevant results.
"search_results": Results from semantic/keyword matching.
"search_result_size": Size of returned results.
"total_records": Total matching results.

Note: "search_result_size" returns top k results from "total_records".

Step 3 initializes "query_body" and "raw_entities" as empty arrays and array of two products.
Step 5 iterates through "raw_entities" to print and update "query_body".
Step 6 sets variables and calls Watsonx Discovery extension.
Step 7 sets "search_results", "search_result_size", "total_records".
Step 8 prints header for search results and calls "Generate Answer" action.

Generate Answer Action:
Prints various passages based on query.
Step 3 sets variables for documents ingested in WxD.
Step 4 prints raw JSON of Watsonx Discovery search results if "verbose" is true.

Note: Set "es_index_name" to Watsonx Discovery indexing name, "es_query_result_size" for top k results, and "embedding_model" to embedding model name.