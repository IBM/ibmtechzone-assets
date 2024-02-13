import requests
import json
import os
from requests.auth import HTTPBasicAuth

headers={}
body_content={}

url= os.environ["url"]
username= os.environ["username"]
password= os.environ["password"]


def set_header(key, value):
        headers[key]=value

def get_header():
        return headers

def set_bodycontent(key, value):
        body_content[key]=value

def get_bodycontent():
        return body_content

def do_get(url, username, password):
        header=get_header()
        data=get_bodycontent()
        response = requests.get(url, auth=HTTPBasicAuth(username, password),verify=False, headers=header, data=data)
        return response

def do_post(url):
        header=get_header()
        data=json.dumps(get_bodycontent())
        print(data)
        print(header)
        response = requests.post(url, verify=False, headers=header, data=data)
        return response

def print_response(response):
        print(response.status_code)
        print(response.text)



set_header("Accept-Encoding","gzip, deflate, br")
set_header("Content-Type","application/json;charset=UTF-8")
set_header("Accept","application/json, text/plain, */*")
get_header()
set_bodycontent("username",username)
set_bodycontent("password",password)
get_bodycontent()

response = requests.get(url, auth=HTTPBasicAuth(username, password),verify=False, headers=header, data=body_content)

os.environ["RESPONSE_CODE"] = response.status_code
os.environ["RESPONSE_TEXT"] = response.text
