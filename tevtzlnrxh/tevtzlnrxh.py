import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from langchain_core.prompts import PromptTemplate
from langchain_ibm import WatsonxLLM
import re
from typing import Annotated
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Fetch environment variables
api_key = os.getenv("api_key", None)
cloud_url = os.getenv("cloud_url", "https://us-south.ml.cloud.ibm.com")
project_id = os.getenv("project_id", None)

# Set parameters for WatsonxLLM
parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 1600,
    "min_new_tokens": 1,
}

# Initialize WatsonxLLM
watsonx_llm = WatsonxLLM(
    model_id="mistralai/mixtral-8x7b-instruct-v01",
    url=cloud_url,
    project_id=project_id,
    params=parameters,
    apikey=api_key,
)


# Define the data model for URL requests
class UrlRequest(BaseModel):
    url: str


# Function to fetch content from a URL
def fetch_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return response.text
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


# Function to scrape and extract text content from HTML
def scrape_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    paragraphs = soup.find_all("p")
    content = "\n".join([para.get_text() for para in paragraphs])
    return content


# Function to preprocess text by cleaning up whitespace
def preprocess_text(text):
    text = re.sub(r" +", " ", text)  # Replace multiple spaces with a single space
    text = re.sub(
        r"\n +", "\n", text
    )  # Remove leading spaces at the beginning of lines
    text = re.sub(
        r"\n\n\n+", "\n\n", text
    )  # Replace multiple newlines with a single newline
    return text.strip()


@app.post("/summarize/")
async def summarize_url(url: UrlRequest):
    html_content = fetch_url_content(url.url)

    if html_content:
        content = scrape_content(html_content)
        content = preprocess_text(content)
    else:
        # Raise an HTTP exception if the URL content could not be retrieved
        raise HTTPException(
            status_code=404, detail="Failed to retrieve content from the URL"
        )

    summary_prompt = '''Generate a concise summary as bullet points of the provided article. Stick closely to the article's content and avoid adding any external details.

Article: """{article}"""

Concise Summary: '''

    template_1 = PromptTemplate.from_template(summary_prompt)

    chain_1 = template_1 | watsonx_llm

    try:
        response = chain_1.invoke(content)
    except Exception as e:
        # Handle any exceptions that occur during the invocation of the model
        raise HTTPException(status_code=500, detail=f"Error generating summary: {e}")

    return {"summary": response}
