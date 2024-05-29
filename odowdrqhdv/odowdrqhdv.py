import requests
import time
from langdetect import detect
from datetime import datetime
import json
import os


bearer_token = "enter your bearer_token"
project_id = "enter your project_id"
def Check_language(response):
        
        if detect_mixed_languages(response) != {"ja"}:
            response_final = trans_jp(response)
            response = response_final
        return response
def trans_jp(text):
        
    start_time=time.time()
    prompt = "下記のテキストを日本語に翻訳する"
    url = self.url
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + bearer_token
    }
    data = {
        "model_id":'meta-llama/llama-2-70b-chat',
        "project_id": project_id,
        "input": prompt + '\n\n' + "Input: " + text + "\n\n" + "Output: ",
        "parameters": {
            "decoding_method": "greedy",
            "min_new_tokens": 1,
            "max_new_tokens": 300,
            "beam_width": 1
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    response = response.json()["results"][0]["generated_text"]
    return response

#detects the language used 
def detect_mixed_languages(text):
    languages = set()
    chunks = text.split(" ")  
    for chunk in chunks:
        language = detect(chunk)
        languages.add(language)
    return languages


Check_language("Enter your text here")