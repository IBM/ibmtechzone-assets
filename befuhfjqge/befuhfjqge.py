import requests
import json
import os

from requests.auth import HTTPBasicAuth

url= os.environ["url"]
header= os.environ["headers"]
username= os.environ["username"]
password= os.environ["password"]
body_content= os.environ["body_content"]

response = requests.get(url, auth=HTTPBasicAuth(username, password),verify=False, headers=header, data=body_content)
os.environ["RESPONSE_CODE"] = response.status_code
os.environ["RESPONSE_TEXT"] = response.text
