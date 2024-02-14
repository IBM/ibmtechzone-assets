import uuid
import time
import requests
import configparser
import os
import json

cp4d_url = os.environ["cp4d_url"]
project_name = os.environ["project_name"]

config = configparser.ConfigParser()
config.read('cp4d_info.conf')
token=config['CP4D']['TOKEN']

def create_container(platformURL, token, is_cloud, container_name, container_type, project_storage_crn):
  print("\nCreating project {}".format(container_name))
  project = None

  if is_cloud == False:
    # TODO once the project team make fix need to change the url to '{}/transactional/v2/projects'
    url = '{}/transactional/v2/projects'.format(platformURL)
    # These ids are auto-generated GUID - which can be random
    storage = {'type': 'assetfiles', 'guid': str(uuid.uuid4())}
  else:
    if not project_storage_crn:
      raise Exception('Storage crn required to create a cloud project')
    crn = project_storage_crn.split(':')
    if len(crn) < 3:
      raise Exception('Storage guid cannot be parsed from storage crn')
    project_storage_guid = crn[len(crn) - 3]
    storage = {'type': 'bmcos_object_storage', 'guid': project_storage_guid, 'resource_crn': project_storage_crn}

  if (container_type == "CONTAINER_PROJECT"):
    url = '{}/transactional/v2/projects'.format(platformURL)
  elif (container_type == CONTAINER_SPACE):
    url = '{}/v2/spaces'.format(platformURL)
  iam_token = token
  headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': "ZenApiKey "+iam_token}
  payload = {'name': container_name, 'generator': 'DataStage', 'storage': storage}
  #headers = create_headers(token)
  start = time.time()
  print(url)
  print(headers)
  print(payload)
  response = requests.post(url, headers=headers, json=payload, verify=False, timeout=180)
  elapsed = time.time() - start
  if not (response.status_code == 201 or response.status_code == 202):
    print('Failed to create project: {}'.format(container_name))
    #raise Exception('Failed to create project, url: {} rc: {} {}'.format(url, response.status_code, response.text))
  else:
    print(response)
    print(response.status_code, response.text)
    print(json.dumps(response.json(), indent=2))

create_container(cp4d_url,token,False,project_name,"CONTAINER_PROJECT",'NA')