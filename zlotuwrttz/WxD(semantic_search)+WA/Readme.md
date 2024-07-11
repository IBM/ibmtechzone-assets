Description:
This asset integrates Watsonx Discovery with Watson Assistant for retrieving passages from multi-passage documents, maintaining document structure via Semantic matching search queries.

Instructions for Use:
Input a query related to Watsonx Discovery-ingested documents. The system displays the top 3 passages retrieved for the query. "Verbose" set to true shows the raw JSON response from Watsonx Discovery. Use specified OpenAPI exclusively for creating WxD extensions due to additional parameters.

Explanation:
OpenAPI: Includes "min_score" for filtering search results by minimum score.

Watsonx Discovery Search Action:
"query_text": User query.
"knn_body": Semantic matching using KNN.
"set_source": Set to avoid extra fields.
"set_min_score": Set minimum score for relevant results.
"search_results": Semantic/keyword matching results.
"search_result_size": Size of returned results.
"total_records": Total matching results.

Note: "search_result_size" returns top k results from "total_records".

Step 3 sets "knn_body", "set_source", and "set_min_score" variables; WxD extension is called.
Step 4 sets "search_results", "search_result_size", "total_records".
Step 5 prints header for search results and calls "Generate Answer" action.

Generate Answer Action:
Prints various passages based on query.
Step 3 sets variables for documents ingested in WxD. Make changes according to requirements.
Step 4 prints raw JSON of Watsonx Discovery search results if "verbose" is true.

Note: Set "es_index_name" to Watsonx Discovery indexing name, "es_query_result_size" for top k results, and "embedding_model" to embedding model name.