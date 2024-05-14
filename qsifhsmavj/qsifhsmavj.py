import requests
import pprint
import os
import ast
# add
api_key = os.environ["api_key"]
project_id = os.environ["project_id"]
job_name = os.environ["job_name"]
job_env_variables = os.environ["job_env_variables"]
job_env_variables=ast.literal_eval(job_env_variables)

url = "https://iam.cloud.ibm.com/identity/token"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

data = {
    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
    "apikey": api_key
}

response = requests.post(url, headers=headers, data=data, verify=False)
access_token = response.json()['access_token']
print(access_token)



headers = {'authorization': 'Bearer %s'%(access_token),
           'content-type': 'application/json'}

host = 'https://api.dataplatform.cloud.ibm.com'

r = requests.get(host+"/v2/jobs",
                 headers=headers,
                 verify=False,
                 params={"project_id": project_id}
                )
result = dict(r.json())
# print(result)
job_id = None
job_id = [ val["metadata"]["asset_id"] for val in result["results"] if val["metadata"]["name"] ==job_name][0]


print("job_name: ", job_name)
print("job_id: ", job_id )


data = {"job_run": {'configuration': {
                                          'env_variables':job_env_variables }}}
        
headers = {'authorization': 'Bearer %s'%(access_token),
           'content-type': 'application/json'}
url = host+"/v2/jobs/{}/runs?project_id={}".format(job_id,project_id)
r = requests.post(url,
                 headers=headers,
                 verify=False,
                 json= data,
                )
pprint.pprint(r.json())
#wait for completion eta 2 min