import streamlit as st
from ibm_watson_machine_learning.foundation_models import Model
import requests
from typing import Optional
import config  # Import the configuration file

# Function to get WatsonX credentials
def get_credentials():
    return {
        "url": config.WATSONX_URL,
        "apikey": config.WATSONX_API_KEY
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
watsonx_api_connection = WatsonXAPIConnection(
    config.WATSONX_MODEL_ID,
    config.WATSONX_PARAMETERS,
    project_id=config.WATSONX_PROJECT_ID,
    apikey=config.WATSONX_API_KEY,
    credentials=credentials
)
print("model is initialized....")

# Initialize GoogleSearch instance
google_search_instance = GoogleSearch(config.GOOGLE_API_KEY, config.GOOGLE_ENGINE_ID)
print("google search engine initialized...")

# Streamlit app
st.set_page_config(
    page_title="LLM With Google Search Demo",
    page_icon=":robot_face:",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Sidebar
st.sidebar.header("Settings")
st.sidebar.write("Adjust the model parameters or other settings here.")

# Main Interface
st.title("LLM With Google Search Demo")
st.write(
    """
    This demo combines IBM Watson's large language model capabilities with Google Search results to provide comprehensive responses.
    """
)

# Layout with columns
col1, col2 = st.columns([3, 1])

# User input for query
with col1:
    user_query = st.text_input("Enter your query:", "")

with col2:
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

# Add some styling
st.markdown(
    """
    <style>
    .stTextInput, .stButton {
        margin-top: 20px;
    }
    .stMarkdown {
        margin-top: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
