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

all_user_info=json.loads(response.text)
print("Users in this CP4D cluster")  
print("==========================")

if os.path.exists("cp4d_users.txt"):
  os.remove("cp4d_users.txt")

f = open("cp4d_users.txt", "a")
f.write("user_name"+"\n")

for user in range(len(all_user_info)):
    print(all_user_info[user]["username"])
    f.write(all_user_info[user]["username"]+"\n")

print("==========================")
f.close()
