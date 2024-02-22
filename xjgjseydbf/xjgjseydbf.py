#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import requests
import json
import random
import time
import configparser
import warnings
warnings.filterwarnings('ignore')

# Provide a timeout value in minutes
# This is how long this script will wait for an MDI job to complete.
# If MDI job run is not complete within 40 minutes, it is stopped and cleared
timeout = 40

def getCPDtoken(cpd_url,cpd_username,cpd_apikey):
    # get token
    url = cpd_url + '/icp4d-api/v1/authorize'
    header = {'Content-Type': 'application/json'}
    data = {'username':cpd_username,'api_key': cpd_apikey}

    try:
        response = requests.post(url,headers=header,json=data,verify=False)
        print(response)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Failed to obtain Cloud Pak for Data authentication token. ERROR: ", err)
        return -1
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("Failed to obtain Cloud Pak for Data authentication token. ERROR: ", e)
        return -1
    mltoken = response.json()["accessToken"]

    return mltoken

# Not needed if project id provided
def getProjectID(projectName):
# Endpoint for getting All projects defined on the platform
    url = f'{cpd_url}/v2/projects'

    # token to authenticate to the platform
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}

    # GET all projects
    try:
        response = requests.get(url,headers=header,verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Failed to get list of Catalogs defined in WKC. ERROR: ", err)
        return -1
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("Failed to get list of Catalogs defined in WKC. ERROR: ", e)
        return -1

    projectsList = response.json()
    #return projectsList
    for p in projectsList['resources']:
        if p['entity']['name'] == projectName:
            return p['metadata']['guid']
    print("Project: ", projectName, " not found")

    return -1


# Not needed if project id provided
def getProjectID(projectName):
# Endpoint for getting All projects defined on the platform
    url = f'{cpd_url}/v2/projects'

    # token to authenticate to the platform
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}

    # GET all projects
    try:
        response = requests.get(url,headers=header,verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Failed to get list of Catalogs defined in WKC. ERROR: ", err)
        return -1
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("Failed to get list of Catalogs defined in WKC. ERROR: ", e)
        return -1

    projectsList = response.json()
    #return projectsList
    for p in projectsList['resources']:
        if p['entity']['name'] == projectName:
            return p['metadata']['guid']
    print("Project: ", projectName, " not found")

    return -1

# Get catalog ID from catalogName
def getCatalogID(catalogName):
    # Endpoint for getting All catalogs defined on the platform
    url = f'{cpd_url}/v2/catalogs'

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

    catalogsList = response.json()
    for c in catalogsList['catalogs']:
        if c['entity']['name'] == catalogName:
            return c['metadata']['guid']
    print("Catalog: ", catalogName, " not found")

    return -1


def getJobs(projectID):
    # Endpoint for getting All projects defined on the platform
    url = f'{cpd_url}/v2/jobs?project_id={projectID}'

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

    jobsList = response.json()
    return jobsList
    
#GET /v2/jobs/{job_id}
def getJobDetails(jobID,projectID):
    # Endpoint for getting All projects defined on the platform
    url = f'{cpd_url}/v2/jobs/{jobID}?project_id={projectID}'

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

    jobDetails = response.json()
    return jobDetails

#/v2/jobs/{job_id}/runs
def getJobRuns(jobID,projectID):
    # Endpoint for getting All projects defined on the platform
    url = f'{cpd_url}/v2/jobs/{jobID}/runs?project_id={projectID}'

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

    jobRuns = response.json()
    return jobRuns

# schemaName is the name of the schema to be used as scope for metadata import job
def createMDI(mdi_name,schemaName,connectionID,projectID):
    #mdi_name=f'{schemaName}-mdi'
    job_name=f'{mdi_name}-job'

    url = f'{cpd_url}/v2/metadata_imports?project_id={projectID}'
    
    header = {'Content-Type': 'application/json', 'Authorization': '' + token}
    
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
    print("header: ", header)
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
    print("header: ", header)
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
    print("about to run mdi for "+mdiName+"  " + schemaName + "  "+connection_id+" "+project_id)
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

# Define global variables for the script
config = configparser.ConfigParser()
config.read('cp4d_info.conf')

cpd_url=config['CP4D']['CPD_URL']
cpd_username=config['CP4D']['CPD_USERNAME']
cpd_apikey=config['CP4D']['CP4D_APIKEY']

token=getCPDtoken(cpd_url,cpd_username,cpd_apikey) #config['CP4D']['CPD_TOKEN']
print("Auth token=" + token)

cpd_project="DataGovernance" #os.environ["cpd_project"]
project_id=config['CP4D']['CPD_PROJECT_ID']
connectionName="pgsql_datasource"

connection_id=config['CP4D']['CONNECTION_ID']

mdiName="pgsql_metadata_import"

schema="gosalesdw"
print("Setting up MDI for schema: ", schema)
mdi_response = setupRunMDI(mdiName,schema)
print("MDI response: ", mdi_response)

# ## END
