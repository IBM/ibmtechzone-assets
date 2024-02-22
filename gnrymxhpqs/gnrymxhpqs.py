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

# Define global variables for the notebook
mdi_id="3b59fb44-5a91-4183-bae0-fb7f31576afe"

cpd_url="https://cpd-cpd-instance.apps.cpd47top.tec.ihost.com"
cpd_username="cpadmin"
cpd_password="TOPaccess1"

projectName="deepak"
project_id="e0756b69-fbf5-47f1-84fe-c68030bf7275"
connectionName="mypg"
connection_id="d8d52de8-6d52-41f0-99e6-ed6ad1efebab"
mdiName="mymdi"
mdeName="mymde2"

# Return a Cloud Pak for Data token needed for executing subsequent APIs
def getCPDtoken(cpd_url,cpd_username,cpd_password):
    # get token
    url = cpd_url + '/v1/preauth/validateAuth'

    try:
        response = requests.get(url,auth=(cpd_username,cpd_password),verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Failed to obtain Cloud Pak for Data authentication token. ERROR: ", err)
        return -1
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("Failed to obtain Cloud Pak for Data authentication token. ERROR: ", e)
        return -1
    mltoken = response.json()["accessToken"]

    return mltoken

# Get Bearer token
token = getCPDtoken(cpd_url,cpd_username,cpd_password)

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

def getUncategorizedID():
    
    url = f'{cpd_url}/v3/categories/uncategorized'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    
    try:
        response = requests.get(url, headers=header,verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("ERROR: ", err)
        return -1
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("ERROR: ", e)
        return -1
    results = json.loads(response.text)
    
    uncategorizedID = results['metadata']['artifact_id']
    return uncategorizedID

# schemaName is the name of the schema to be used as scope for metadata import job
def createMDE(mdeName,projectID,mdiID,cID):
    mde_name=f'{mdeName}'
    
    url = f'{cpd_url}/v2/metadata_enrichment/metadata_enrichment_area?project_id={projectID}'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    #mde_name="testMDEapi"
    #schemaName="CUSTOMER"
    
    objective = {
        "enrichment_options": {
            "structured": {
                "profile": True,
                "assign_terms": True,
                "analyze_quality": True
            }
        },
        "governance_scope": [
            {
                'type': 'CATEGORY',
                'id': cID
            }
        ],
        "sampling": {
            "structured": {
                "project_default_settings": True,
                "method": "RANDOM",
                "analysis_method": "FIXED",
                    "sample_size": {
                    "name": "BASIC"
                }
            }
        },
        "datascope_of_reruns": "ALL"
    }
         
    data_scope = {
        "container_assets": {
            "metadata_import": [mdiID]
        }
    }
    payload = {
        "name": mde_name,
        "description": f"metadata enrichment",
        "objective": objective,
        "data_scope": data_scope
    }

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


# In[37]:
config = configparser.ConfigParser()
config.read('cp4d_info.conf')

cID = getUncategorizedID()
response=createMDE(mdeName,project_id,mdi_id,cID)
print("response: ", response)
