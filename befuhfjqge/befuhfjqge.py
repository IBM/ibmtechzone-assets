import requests
import json
import os
import configparser
import pandas as pd
from io import StringIO

headers={}
body_content={}
config = configparser.ConfigParser()
config.read('cp4d_info.conf')
token=config['CP4D']['TOKEN']
cp4d_url= os.environ["cp4d_url"]+"/usermgmt/v1/usermgmt/users?includeAll=true"

def set_header(key, value):
        headers[key]=value

def get_header():
        return headers

def set_bodycontent(key, value):
        body_content[key]=value

def get_bodycontent():
        return body_content

def do_get(url):
        header=get_header()
        response = requests.get(url, verify=False, headers=header)
        return response

def print_response(response):
        print(response.status_code)
        print(response.text)


set_header("Authorization","ZenApiKey "+token)
get_header()

response = do_get(cp4d_url)

pd.json_normalize(response.text, max_level=1)
  
