def watsondiscovery_utils():
    from IPython import get_ipython 
    from ibm_watson import DiscoveryV2
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    
    url = <>
    api_key=<>
    project_id=<>
    authenticator = IAMAuthenticator(api_key)
    discovery = DiscoveryV2(
        version='2020-08-30',
        authenticator=authenticator
        )
    discovery.set_service_url(url)
    discovery.set_disable_ssl_verification(True)

    def score(payload):               
        queries = payload.get("input_data")[0].get("values")[0][0]
        if len(payload.get("input_data")[0].get("values")[0])>1:
            max_counts = payload.get("input_data")[0].get("values")[0][1]
        else:
            max_counts = [5 for _ in range(len(queries))]
        retrievals = []
        for query_index in range(len(queries)):
            retrievals.append(discovery.query(
                project_id = project_id,
                count=max_counts[query_index],
                #collection_ids= ['aff9642c-d86a-ca00-0000-018ccdf06c2b'],
                natural_language_query= queries[query_index], ## The text or the keywords which is being looked for
                highlight=True, 
                passages= {'QueryLargePassages': True, 'per_document': True} ##This will only return the passage of the document and rank it based on the relevance
                ).get_result()) 
       
        # Score using the pre-defined model
        score_response = {
            'predictions': [{
                'fields': ['retrievals'], 
                'values': [[retrievals]]
                }]
        } 
        return score_response

    return score


score = watsondiscovery_utils()