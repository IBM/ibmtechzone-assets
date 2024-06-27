import os
import pandas as pd
import json
from dotenv import load_dotenv
from typing import Any, List, Mapping, Optional, Union, Dict
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from genai.credentials import Credentials
from genai import Client
from genai.extensions.langchain import LangChainInterface

class SentimentAnalyzer:
    def __init__(self, api_key: str, api_endpoint: str, model_id: str):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.model_id = model_id
        self.bam_creds = Credentials(api_key=self.api_key, api_endpoint=self.api_endpoint)
        self.bam_params = {
            "decoding_method": "greedy",
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 100,
            "random_seed": 50,
            "min_new_tokens": 1,
            "max_new_tokens": 1000
        }
        self.llm = LangChainInterface(
            model_id=self.model_id, 
            parameters=self.bam_params, 
            client=Client(credentials=self.bam_creds)
        )
        self.sentiment_prompt_template = self._create_sentiment_prompt_template()
        self.sentimentintentchain = LLMChain(llm=self.llm, prompt=self.sentiment_prompt_template)

    def _create_sentiment_prompt_template(self) -> PromptTemplate:
        sentiment_prompt = (
            """
            <<SYS>> 
            You are an expert at performing sentiment analysis on the given text. Your goal is to classify the text based on the mood or mentality expressed in the text.
            <<SYS>>

            [INST]
            - First take a look at the given text {{text}}
            - Perform the sentiment analysis on it. 
            - Sentiment analysis is the process of classifying whether a block of text is positive, negative, or neutral.
            - It focuses not only on polarity (positive, negative & neutral) but also on emotions (happy, sad, angry, etc.).
            - Focus mainly on Emotion Detection and Intent Analysis 
            - Emotion detection: This aims to detect emotions like happiness, frustration, anger, sadness, etc.
            - Intent Analysis: Aims to understand the user’s intention behind a certain statement. For example, a statement like “I would need a car” might indicate a purchasing intent.
            - Sentiments could be of different types, look through these different types and use it to understand the situation. 
            - Sentiments could be Positive, Negative, or Neutral:
            - Positive sentiments are feelings or opinions that are generally favorable, such as happiness, joy, excitement, or admiration.
            - Negative sentiments are those that express dissatisfaction, sadness, anger, frustration, or criticism.
            - Neutral sentiments indicate a lack of strong feelings or opinions on a matter; the text is factual, objective, or indifferent.
            - Compound Sentiments - This involves breaking down text not just into positive, negative, and neutral, but also measuring the intensity or degree of emotion. For instance, sentiments could be very positive, moderately positive, slightly positive, neutral, slightly negative, moderately negative, and very negative.
            - Now based on the above sentiments, read through the entire text by considering it as one and then perform the sentiment analysis.
            - Think step by step
            - My output should only include the sentiments, emotions, and intent that has been extracted by considering the entire text as one. It should not include any explanation.
            - Give me the sentiment analysis, emotions, and the intent along with their percentages in the output
            [/INST]
            analysis:

            {{text}}
            analysis:
            """
        )
        return PromptTemplate(input_variables=["text"], template=sentiment_prompt)

    def analyze_sentiment(self, text: str) -> str:
        result = self.sentimentintentchain.invoke({'text': text}).get('text')
        return result

# Usage
load_dotenv()
bam_api_key = os.environ("bam_api_key")
bam_api_endpoint = "https://bam-api.res.ibm.com"
model_id = "mistralai/mistral-7b-instruct-v0-2"

analyzer = SentimentAnalyzer(api_key=bam_api_key, api_endpoint=bam_api_endpoint, model_id=model_id)
data_new = os.environ("Enter text")
description_new = analyzer.analyze_sentiment(data_new)
print(description_new)
