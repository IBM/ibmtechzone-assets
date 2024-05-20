import PyPDF2
import io 
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import pandas as pd
import re
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
project_id = os.getenv("PROJECT_ID", None)

def textToTable(text):
  lines = text.split('\n')
  data = {'Metric': []}
  if 'FY24E' in text:
    data['FY24E'] = []
  if 'FY25E' in text:
    data['FY25E'] = []

  year = None

  for line in lines:
      if 'FY' in line:
          year = re.findall(r'\b\w*FY\w*\b', text)[0]
      elif ':' in line:
          key, value = line.split(':')
          key = key.strip()
          key = re.sub(r'^\d+\.\s*', '', key)
          value = value.strip()
          data['Metric'].append(key)
          if year == 'FY25E':
              data['FY25E'].append(value)
          elif year == 'FY24E':
              data['FY24E'].append(value)

  df = pd.DataFrame(data)
  return df

def LLMresponce(prompt,params):
    creds = {
        "url": ibm_cloud_url,
        "apikey": api_key 
    }

    model = Model(
        model_id = "meta-llama/llama-2-70b-chat",
        # model_id = "ibm/granite-13b-instruct-v2",
        params=params,
        credentials=creds,
        project_id=project_id)
    # print("promot call started ",prompt)
    text = model.generate_text(prompt)
    # print("prompt call ended with responce ",text)
    return text


def extract_paragraphs(uploaded_file):
    reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
    text = []
    for page in range(min(len(reader.pages), 3)):
        page_text = reader.pages[page].extract_text()
        if page_text:  
            text.append(page_text)
    return text


if __name__=="__main__":
    params={
    "decoding_method": "greedy",
    # "stop_sequences": [
    #   "\n\n"
    # ],
    "min_new_tokens": 1,
    "max_new_tokens": 10,
    "repetition_penalty": 1.25,
    "moderations": {
      "hap": {
        "input": "false",
        "threshold": 0.75,
        "output": "false"
      }
    }
  }
    print(LLMresponce("hi",params))