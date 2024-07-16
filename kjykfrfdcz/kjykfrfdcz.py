def generate_answer_wml(context, query):
    load_dotenv()
    API_KEY = os.getenv("API_KEY",None)
    token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
    API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
    mltoken = token_response.json()["access_token"]
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
    # NOTE: manually define and pass the array(s) of values to be scored in the next line
    
    scoring_data = {
        "parameters": {
            "prompt_variables": {
                "context_document": f"{context}",
                "query": query
            }
        }
    }
    response_scoring = requests.post("<your-api-endpoint>", json=scoring_data,
    headers={'Authorization': 'Bearer ' + mltoken})
 
    data = response_scoring.json()
    return data['results'][0]['generated_text']