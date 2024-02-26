import time
import requests
import configparser
import os
import json

cp4d_url = os.environ["cp4d_url"]
cp4d_username = os.environ["cp4d_username"]
cp4d_displayname = os.environ["cp4d_displayname"]
cp4d_password = os.environ["cp4d_password"]
cp4d_roles = os.environ["cp4d_roles"]

config = configparser.ConfigParser()
config.read('cp4d_info.conf')
token=config['CP4D']['TOKEN']

def create_user(platformURL, token, username, displayname, password, roles):
  print("\nCreating User {}".format(username))

    url = '{}/transactional/v2/projects'.format(platformURL)
    iam_token = token
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': "ZenApiKey "+iam_token}
    payload = {'name': container_name, 'generator': 'DataStage', 'storage': storage}
    start = time.time()
    print(url)
    print(headers)
    print(payload)
    response = requests.post(url, headers=headers, json=payload, verify=False, timeout=180)
    elapsed = time.time() - start
    if not (response.status_code == 201 or response.status_code == 202):
      print('Failed to create user: {}'.format(username))
    else:
      print(response)
      print(response.status_code, response.text)
      print(json.dumps(response.json(), indent=2))

create_user(cp4d_url, token, cp4d_username, cp4d_displayname, cp4d_password, cp4d_roles)