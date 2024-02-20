import os
import pandas as pd
import requests
import json
import random
import time

import warnings
warnings.filterwarnings('ignore')
project_name=os.environ["project_name"]
connection_name=os.getenv("connection_id")
mdi_name=os.getenv("mdi_name")

token=os.environ["token"]
# schemaName is the name of the schema to be used as scope for metadata import job
def createMDI(mdi_name,schemaName,connectionID,projectID):
    #mdi_name=f'{schemaName}-mdi'
    job_name=f'{mdi_name}-job'

    url = f'{cpd_url}/v2/metadata_imports?project_id={projectID}'
    
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    
    payload = {
        "name": mdi_name,
        "description": f"metadata import for schema {schemaName}",
        "import_type": "metadata",
        "connection_id": connectionID,
        "target_project_id": projectID,
        "scope": {"paths": [f"/{schemaName}"]}
    }
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print("Creating MDI object for schema: ", schemaName)
    print("Create MDI API url: ", url)
    print("payload: ", payload)
    
    try:
        response = requests.post(url, json=payload, headers=header,verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("ERROR: ", err)
        return -1
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("ERROR: ", e)
        return -1
    results = json.loads(response.text)
    
    return results

# schemaName is the name of the schema to be used as scope for metadata import job
def createMDIjob(mdiName,schemaName,projectID,mdiID):
    
    url = f'{cpd_url}/v2/jobs?project_id={projectID}' 
    
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    
    
    job_name = f'{mdiName}-job'

    payload = {
        "job": {
            "asset_ref": f"{mdiID}",
            "name": job_name,
            "configuration": {},
            "description": f"Metadata Import job for schema: {schemaName}"
        }
    }
    print("#################################")
    print("Creating MDI job, ", job_name, " for schema: ", schemaName)
    print("Create MDI Job API url: ", url)
    print("payload: ", payload)
    
    try:
        response = requests.post(url, json=payload, headers=header,verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("ERROR: ", err)
        return -1
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("ERROR: ", e)
        return -1
    results = json.loads(response.text)
    
    return results

# patch MDI
# PATCH: https://<cpd-url>/v2/metadata_imports/<metadata import id>?project_id=<project-id>
#{
# "job_id":"<job-id>"
#}
def patchMDI(mdiID,jobID,projectID):
    url = f'{cpd_url}/v2/metadata_imports/{mdiID}?project_id={project_id}'

    header = {'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}

    payload = {
        "job_id": jobID
    }
    
    print("payload: ", payload)

    try:
        response = requests.patch(url, json=payload, headers=header,verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("response: ", response.text)
        print("ERROR: ", err)
        return -1
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("ERROR: ", e)
        return -1

    results = json.loads(response.text)

    return results

# create job run for MDI
def createMDIjobRun(jobID,projectID):
    
    url = f'{cpd_url}/v2/jobs/{jobID}/runs?project_id={projectID}&job_id={jobID}'
    
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    
    payload = {
        "job_run": {}
    } 
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print("Create MDI Job Run API url: ", url)
    print("payload: ", payload)
    
    try:
        response = requests.post(url, json=payload, headers=header,verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("ERROR: ", err)
        return -1
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("ERROR: ", e)
        return -1
    results = json.loads(response.text)
    
    return results

#/v2/jobs/{job_id}/runs/{run_id}
def getJobRunState(jobID,jobrunID,projectID):
    # Endpoint for getting All projects defined on the platform
    url = f'{cpd_url}/v2/jobs/{jobID}/runs/{jobrunID}?project_id={projectID}'

    # token to authenticate to the platform
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}

    # GET all catalogs
    try:
        response = requests.get(url,headers=header,verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Failed to get list of Catalogs defined in WKC. ERROR: ", err)
        return -1
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("Failed to get list of Catalogs defined in WKC. ERROR: ", e)
        return -1

    jobrun_results = response.json()
    return jobrun_results

#/v2/jobs/{job_id}/runs/{run_id}
def cancelJobRun(jobID,jobrunID,projectID):
    # Endpoint for getting All projects defined on the platform
    url = f'{cpd_url}/v2/jobs/{jobID}/runs/{jobrunID}/cancel?project_id={projectID}'

    # token to authenticate to the platform
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}

    payload = {}

    
    try:
        response = requests.post(url, json=payload, headers=header,verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("ERROR: ", err)
        return -1
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("ERROR: ", e)
        return -1
    results = json.loads(response.text)
    
    return results


def setupRunMDI(mdiName,schemaName):
    # Create MDI and capture the id of the created MDI
    #mdi_response=createMDI(schemaName,connection_id,project_id,target_catalog_id)
    mdi_response=createMDI(mdiName,schemaName,connection_id,project_id)
    mdi_id = mdi_response["metadata"]["asset_id"]
    schema_mdi_name = mdi_response["entity"]["name"]
    # Create MDI job associated with the MDI created earlier and capture job id
    mdi_job_results = createMDIjob(mdiName,schemaName,project_id,mdi_id)
    mdi_job_id = mdi_job_results["metadata"]["asset_id"]
    schema_mdi_job_name = mdi_job_results["metadata"]["name"]
    # Patch MDI with created jobID
    patch_mdi_results = patchMDI(mdi_id,mdi_job_id,project_id)
    # Trigger a job run of the specified ID
    mdi_job_run_results = createMDIjobRun(mdi_job_id,project_id)
    job_run_id = mdi_job_run_results["metadata"]["asset_id"]
    job_run_state = mdi_job_run_results["entity"]["job_run"]["state"]
    schema_mdi_job_run_name = mdi_job_run_results["metadata"]["name"]
    # Get job run status and keep checking until status complete
    while job_run_state != 'Completed':
        localtime = time.localtime()
        result = time.strftime("%I:%M:%S %p", localtime)
        print("waiting for 60 seconds, time: ", result)
        time.sleep(60)
        job_run_results = getJobRunState(mdi_job_id,job_run_id,project_id)
        job_run_state = job_run_results["entity"]["job_run"]["state"]
    
        job_run_duration = job_run_results["entity"]["job_run"]["duration"]
        # If job takes a long time before completing, cancel
        # This accounts for potential issues with some running jobs
        if job_run_duration > 60*timeout:
            print("Cancelling job run with id: ", job_run_id, " for schema: ", schemaName, " because it is taking more than ", timeout, " minutes")
            schema_mdi_status = 'FAILED'
            cancelJobRun(mdi_job_id,job_run_id,project_id)
            break
    print("Successful job run with id: ", job_run_id, " for schema: ", schemaName)
    schema_mdi_status = 'COMPLETED'
    statusResponse = [schemaName,schema_mdi_name,mdi_id,schema_mdi_job_name,mdi_job_id,schema_mdi_job_run_name,job_run_id,schema_mdi_status]
    return statusResponse
    

mdiName=os.getenv("MDI_NAME")
schema=os.getenv("SCHEMA")
print("Setting up MDI for schema: ", schema)
mdi_response = setupRunMDI(mdiName,schema)
print("MDI response: ", mdi_response)
