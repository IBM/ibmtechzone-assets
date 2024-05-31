import os
from ibm_watson_machine_learning.foundation_models import Model
import streamlit as st
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_credentials():
    return {
        "url": os.getenv("IBM_CLOUD_URL"),
        "apikey": os.getenv("IBM_CLOUD_APIKEY")
    }

def send_to_watsonxai(prompt, model_id="google/flan-ul2", max_new_tokens=3):
    parameters = {
        "decoding_method": "sample",
        "temperature": 0,
        "top_p": 1,
        "top_k": 10,
        "random_seed": 42,
        "max_new_tokens": max_new_tokens,
        "repetition_penalty": 1
    }
    project_id = os.getenv("PROJECT_ID")

    model = Model(
        model_id=model_id,
        params=parameters,
        credentials=get_credentials(),
        project_id=project_id
    )
    generated_response = model.generate_text(prompt)
    return generated_response

def clean_response(response):
    # Remove unwanted tags
    cleaned_response = re.sub(r"<.*?>", "", response)
    return cleaned_response.strip()

def final(user_input):
    prompt = f"""
<s>[INST] <<SYS>>
Objective: Analyze customer conversation summaries to extract sentiment, categorizing as positive or negative. This aims to understand customer feedback and emotions, enhancing the ability to gauge overall satisfaction and identify improvement areas.

Process:
1. Analyze Summaries: Examine customer conversation summaries to identify key sentiments. Pay attention to words, phrases, and context indicating satisfaction or dissatisfaction.
2. Categorize Sentiment: Classify sentiments as positive or negative using NLP techniques and predefined indicators.
3. Verify Sentiment: Review categorized sentiments for accuracy, ensuring alignment with the conversation context and tone.

Examples:
1. Customer Service Feedback: Determine overall sentiment and identify satisfaction patterns or issues.
2. Product Reviews: Gauge customer opinions and identify common themes.
3. Support Calls: Understand customer frustrations or satisfaction with provided solutions.

Guidelines:
1. Accuracy: Ensure precise sentiment identification and categorization.
2. Contextual Understanding: Consider conversation context for accurate sentiment interpretation.
3. Consistency: Maintain consistent sentiment labeling across summaries.
4. Cross-Validation: Validate categorized sentiments with additional methods or tools for reliability.

Resources:
1. NLP Libraries: Utilize libraries like NLTK, TextBlob, spaCy for sentiment analysis.
2. References: Consult sentiment analysis resources to enhance accuracy.

Deliverable:
Generate a one-word categorization for each conversation summary as either positive or negative. Provide no additional information.
Input: {user_input}
Output:
"""
    response = send_to_watsonxai(prompt)
    return clean_response(response)

# Streamlit UI
st.set_page_config(page_title="Sentiment Analysis", layout="centered")

# Display banner image (replace with your own image path if needed)
st.image("banner1.jpg")

# Title and description
st.markdown("<center><span style='font-size: 26px; font-weight: bold;'>Sentiment Analysis</span></center>", unsafe_allow_html=True)

# Text input for the customer conversation summary
user_input = st.text_area("Customer conversation summary", placeholder="Paste conversation summary here")

# Button to analyze sentiment
if st.button("Analyze"):
    if user_input:
        result = final(user_input)
        st.text_area("Sentiment analysis results", value=result, height=100)
    else:
        st.warning("Please enter a conversation summary to analyze.")
