import time
from langdetect import detect
from datetime import datetime
import json
import os


bearer_token = "enter your bearer_token"
project_id = "enter your project_id"
url = "enter the url here"
def Check_language(response):
        
        if detect_mixed_languages(response) != {"ja"}:
            response_final = trans_jp(response)
            response = response_final
        return response

def trans_jp(text):
        
    prompt = "下記のテキストを日本語に翻訳する"
    "use  LLM for translating the text"
    translated_response = "translated using LLM"
    return translated_response

#detects the language used 
def detect_mixed_languages(text):
    languages = set()
    chunks = text.split(" ")  
    for chunk in chunks:
        language = detect(chunk)
        languages.add(language)
    return languages


Check_language("Enter your text here")