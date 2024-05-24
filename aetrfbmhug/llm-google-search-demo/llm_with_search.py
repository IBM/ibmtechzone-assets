import streamlit as st
from ibm_watson_machine_learning.foundation_models import Model
import requests
from typing import Optional

# Function to get WatsonX credentials
def get_credentials():
    return {
        "url": "https://us-south.ml.cloud.ibm.com",
        "apikey": "RMiQPXL35rIdHctmsD0wEtd1hkCAeqNynuw1ap41Gb5C"
    }

class WatsonXAPIConnection:
    def __init__(self, model_id, parameters, project_id=None, space_id=None, apikey=None, credentials=None):
        self.model_id = model_id
        self.parameters = parameters
        self.project_id = project_id
        self.space_id = space_id
        self.apikey = apikey
        self.credentials = credentials
        self.model = self._initialize_model()

    def _initialize_model(self):
        return Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials=self.credentials,
            project_id=self.project_id,
            space_id=self.space_id
        )

    def generate_response(self, prompt_input):
        print("Submitting generation request...")
        generated_response = self.model.generate_text(prompt=prompt_input)
        return generated_response

class GoogleSearch:
    def __init__(self, api_key, engine_id):
        self.api_key = api_key
        self.engine_id = engine_id

    def search(self, query, num_results=10):
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': self.api_key,
            'cx': self.engine_id,
            'num': num_results
        }
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        search_results = response.json().get('items', [])
        text_results = []
        for result in search_results:
            title = result.get('title')
            snippet = result.get('snippet')
            link = result.get('link')
            text_results.append({'title': title, 'snippet': snippet, 'link': link})
        return text_results

    def process_query(self, query):
        print("query:", query)
        results = self.search(query)
        test = ""
        result_links = ""
        for result in results:
            test += f"title: {result['title']} \n"
            test += f"snippet: {result['snippet']}\n\n"
            result_links += f"link: {result['link']} \n"

        with open("g_search_snippets.txt", 'w', encoding='utf-8') as file:
            file.write(test)

        return {"content": test, "result_links": result_links}

# Get WatsonX credentials
credentials = get_credentials()

# Initialization
watsonx_api_connection = WatsonXAPIConnection("meta-llama/llama-2-70b-chat", {"decoding_method": "greedy", "max_new_tokens": 200, "repetition_penalty": 1}, project_id="692851cf-5c7f-4a89-987f-eeaf487133fa", apikey="RMiQPXL35rIdHctmsD0wEtd1hkCAeqNynuw1ap41Gb5C", credentials=credentials)
print("model is initialized....")

# Initialize GoogleSearch instance
google_search_instance = GoogleSearch("AIzaSyBJ4hpT8Ry1iE-5LeAaibSVfPHm9knbrsg", "552f6543e3ef649bc")
print("google search engine initialized...")

# Streamlit app
st.title("LLM With Google Search Demo")

# User input for query
user_query = st.text_input("Enter your query:")

# Process the user query
if st.button("Submit"):
    search_results = google_search_instance.process_query(user_query)
    context = search_results["content"]

    prompt_input = f"""
    You are a helpful, respectful, and honest assistant. Always answer as helpfully as possible, while being safe.
    Generate a clear and concise response by extracting relevant information from the context.
    Make use of context data in prompt input specified as context for generating response.
    Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content.
    Please ensure that your responses are socially unbiased and positive in nature.
    If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct.
    If you don't know the answer to a question, please don't share false information.

    Data: {context}

    Input: {user_query} 
    Output:
    """

    response = watsonx_api_connection.generate_response(prompt_input)

    # Display the response
    st.subheader("Response:")
    st.write(response)
