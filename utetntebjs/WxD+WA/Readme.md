Description:
This asset facilitates the integration of Watsonx Discovery with Watson Assistant to retrieve original passages from documents related to a search query.

Instructions for Use:
You can input a query related to documents ingested in Watsonx Discovery. The system will execute an action to display the maximum number of passages retrieved for that specific query. By setting "Verbose" to true, you can view the raw JSON response from Watsonx Discovery.

Explanation:

Watsonx Discovery Search Action:
The "Watsonx Discovery Search" action involves two key variables: "query_body_generic" and "query_source".
In Step 3, "query_body_generic" and "query_source" are configured, and the Watsonx Discovery extension is invoked.
Step 3 also uses the "query_source" variable, which includes crucial fields such as "result_title_field" and "result_body_field", adjusted as per the document indexing.
In Step 6, results from Watsonx Discovery are stored in the "search_results" variable, followed by the invocation of the "Generate Answer" action.

Generate Answer Action:
In the "Generate Answer" action, various passages are printed based on the provided query.
Step 5 involves printing the raw JSON of search results retrieved from Watsonx Discovery if "verbose" is set to true.

Note: Set "es_index_name" to the indexing name created in Watsonx Discovery and "has_inner_hits" to False.