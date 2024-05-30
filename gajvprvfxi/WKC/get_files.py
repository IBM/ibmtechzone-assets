import Config
import requests
import json

#Code for generating access token using api key
def Generate_Acess_Token():
    payload = f'grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey&apikey={Config.API_KEY}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", Config.TOEKN_URL, headers=headers, data= payload)
    response_dict = json.loads(response.text)
    access_token = response_dict["access_token"]
    return access_token

#code for getting all the assets under given connection and catalog id
def Get_Files():
    url = f"{Config.WKC_URL}/connections/{Config.CONNECTION_ID}/assets?catalog_id={Config.CATALOG_ID}&path="
    payload = {}
    acess_token = Generate_Acess_Token()
    headers = {
        'Authorization': f'Bearer {acess_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    file_list =[]
    response = requests.request("GET", url, headers=headers, data=payload)
    response_dict = json.loads(response.text)
    for i in response_dict['assets']:
        file_list.append(i['id'])
    return file_list

test = Get_Files()
print("testing done", test)
