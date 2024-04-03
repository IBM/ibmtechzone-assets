import pandas as pd
import requests
import json
import asyncio

def make_rag_request(question, ip, port):
    url = f"http://{ip}:{port}/ask"
    headers = {"Content-Type": "application/json"}
    data = {"question": f"{question}"}

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    return response

async def get_rag_responses(questions, ip, port):

    llm_answers = []

    for question in questions:
        response = make_rag_request(question, ip, port)
        llm_answers.append(response.json()['answer'].strip())
        await asyncio.sleep(1)
    return llm_answers
