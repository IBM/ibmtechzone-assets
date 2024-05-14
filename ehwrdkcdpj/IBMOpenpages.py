# %%
import requests
import json
# from scraper import Scraper
import openpagesconfig
import json
from bs4 import BeautifulSoup

# %% [markdown]
# ### Getting data from Legifrance API

# %%
# scraper = Scraper()

'''
Here you need to add the data which needs to be pushed to IBM Openpages
'''


# %% [markdown]
# ### Creation of Mandate
# 

# %%
# Set API endpoint URL
url = 'http://eu-de.services.cloud.techzone.ibm.com:41967/grc/api/contents'

# Set username and password
username = openpagesconfig.username
password = openpagesconfig.password


# Set authentication headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Set request method and data (in this case, it's a POST request with JSON data)
method = 'POST'

# Define the JSON data
json_data = {
    "fields": {
        "field": [
            {
                "id": "681",
                "dataType": "STRING_TYPE",
                "name": "OPSS-Mand:Summary",
                "value": "Test"
            }
        ]
    },
    "typeDefinitionId": "61",
    "parentFolderId": "41872",
    "name": "",
    "description": "Represent external items with which organizations need to comply."
}

# Update the value of "primaryParentID"
json_data["name"] = openpagesconfig.mandate_name


# Send the request
response = requests.request(method, url, headers=headers, json=json_data, auth=(username, password))

# Check if the response was successful (200 OK)
if response.status_code == 200:
    print('Request successful!')

    print("Response: ", response.text)
    # Parse the JSON response
    response_json = json.loads(response.text)

    # Extract the id
    mandate_id = response_json["id"]
    mandate_name = response_json["name"]

    print("Mandate ID:", mandate_id)
    print("Mandate Name:", mandate_name)

else:
    print("Response: ", response.text)
    print(f'Request failed with status code {response.status_code}')

# %% [markdown]
# ### Creation of Sub-mandate

# %%
# Set API endpoint URL
url = 'http://eu-de.services.cloud.techzone.ibm.com:41967/grc/api/contents'

# Set username and password
username = openpagesconfig.username
password = openpagesconfig.password

# Set authentication headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Set request method and data (in this case, it's a POST request with JSON data)
method = 'POST'

# Define the JSON data
json_data = {
  "fields": {
    "field": [
      {
        "id": "1361",
        "dataType": "STRING_TYPE",
        "name": "OPSS-SubMand:Summary Text",
        "value": "TestSubmand1"
      },
      {
        "id": "1359",
        "dataType": "ENUM_TYPE",
        "name": "OPSS-SubMand:Content Source",
        "enumValue": {
                    "name": "Other"
             }
        }
    ]
},
  "typeDefinitionId": "92",
  "parentFolderId": "41872",
  "primaryParentId": "",
  "name": "",
  "description": "Represent external (or internal) sub-items with which the organization needs to comply"
}

# Update the value of "primaryParentID" and "name"
json_data["primaryParentId"] = mandate_id
json_data["name"] = openpagesconfig.submandate_name

# Send the request
response = requests.request(method, url, headers=headers, json=json_data, auth=(username, password))

# Check if the response was successful (200 OK)
if response.status_code == 200:
    print('Request successful!')

    print("Response: ", response.text)
    # Parse the JSON response
    response_json = json.loads(response.text)

    # Extract the id
    Submandate_id = response_json["id"]
    Submandate_name = response_json["name"]
    print("Sub-mandate ID:", Submandate_id)
    print("Sub-mandate Name:", Submandate_name)

else:
    print("Response: ", response.text)
    print(f'Request failed with status code {response.status_code}')

# %% [markdown]
# ### Creation of Requirements1

# %%
# Set API endpoint URL
url = 'http://eu-de.services.cloud.techzone.ibm.com:41967/grc/api/contents'

# Set username and password
username = openpagesconfig.username
password = openpagesconfig.password

# Set authentication headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Set request method and data (in this case, it's a POST request with JSON data)
method = 'POST'

# Define the JSON data
json_data = {
  "fields": {
    "field": [
      {
            "id": "7037",
            "dataType": "MEDIUM_STRING_TYPE",
            "name": "OVIDE-Shared:Content",
            "value": ""
        },
        {
            "id": "7034",
            "dataType": "ENUM_TYPE",
            "name": "OVIDE-Shared:Content HREF",
            "enumValue": {
                    "name": "Yes"
             }
        },
        {
            "id": "7036",
            "dataType": "ENUM_TYPE",
            "name": "OVIDE-Shared:IntegrationStatus",
            "enumValue": {
                    "name": "Brut"
             }
        },
        {
            "id": "7035",
            "dataType": "INTEGER_TYPE",
            "name": "OVIDE-Shared:NB HREF",
            "value": ""
        }
    ]
  },
  "typeDefinitionId": "79",
  "parentFolderId": "41872",
  "primaryParentId": "",
  "name": "",
  "description": "Represents a collection of controls with which an organization must comply"
}

# Update the value of "primaryParentID", "value" and "name"
json_data["primaryParentId"] = Submandate_id
json_data["name"] = openpagesconfig.requirement_name1
json_data['fields']['field'][0]['value'] = html_content_article1
souplen = BeautifulSoup(html_content_article1, 'html.parser'); hyperlinks = souplen.find_all('a'); num_hyperlinks = len(hyperlinks)
json_data['fields']['field'][3]['value'] = num_hyperlinks

# Send the request
response = requests.request(method, url, headers=headers, json=json_data, auth=(username, password))

# Check if the response was successful (200 OK)
if response.status_code == 200:
    print('Request successful!')

    print("Response: ", response.text)
    # Parse the JSON response
    response_json = json.loads(response.text)

    # Extract the id
    requirement_id_1 = response_json["id"]
    requirement_name_1 = response_json["name"]
    print("Requirement1 ID:", requirement_id_1)
    print("Requirement1 Name:", requirement_name_1)

else:
    print("Response: ", response.text)
    print(f'Request failed with status code {response.status_code}')

# %% [markdown]
# ### Creation of Requirements2

# %%
# Set API endpoint URL
url = 'http://eu-de.services.cloud.techzone.ibm.com:41967/grc/api/contents'

# Set username and password
username = openpagesconfig.username
password = openpagesconfig.password

# Set authentication headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Set request method and data (in this case, it's a POST request with JSON data)
method = 'POST'

# Define the JSON data
json_data = {
  "fields": {
    "field": [
      {
            "id": "7037",
            "dataType": "MEDIUM_STRING_TYPE",
            "name": "OVIDE-Shared:Content",
            "value": ""
        },
        {
            "id": "7034",
            "dataType": "ENUM_TYPE",
            "name": "OVIDE-Shared:Content HREF",
            "enumValue": {
                    "name": "Yes"
             }
        },
        {
            "id": "7036",
            "dataType": "ENUM_TYPE",
            "name": "OVIDE-Shared:IntegrationStatus",
            "enumValue": {
                    "name": "Brut"
             }
        },
        {
            "id": "7035",
            "dataType": "INTEGER_TYPE",
            "name": "OVIDE-Shared:NB HREF",
            "value": ""
        }
    ]
  },
  "typeDefinitionId": "79",
  "parentFolderId": "41872",
  "primaryParentId": "",
  "name": "",
  "description": "Represents a collection of controls with which an organization must comply"
}

# Update the value of "primaryParentID" and "name"
json_data["primaryParentId"] = Submandate_id
json_data["name"] = openpagesconfig.requirement_name2
json_data['fields']['field'][0]['value'] = html_content_article3
souplen = BeautifulSoup(html_content_article3, 'html.parser'); hyperlinks = souplen.find_all('a'); num_hyperlinks = len(hyperlinks)
json_data['fields']['field'][3]['value'] = num_hyperlinks

# Send the request
response = requests.request(method, url, headers=headers, json=json_data, auth=(username, password))

# Check if the response was successful (200 OK)
if response.status_code == 200:
    print('Request successful!')

    print("Response: ", response.text)
    # Parse the JSON response
    response_json = json.loads(response.text)

    # Extract the id
    requirement_id_2 = response_json["id"]
    requirement_name_2 = response_json["name"]
    print("Requirement1 ID:", requirement_id_2)
    print("Requirement1 Name:", requirement_name_2)

else:
    print("Response: ", response.text)
    print(f'Request failed with status code {response.status_code}')

# %% [markdown]
# ### Get the Requirements data

# %%
# Set API endpoint URL
url = 'http://eu-de.services.cloud.techzone.ibm.com:41967/grc/api/contents'

# Update the URL with requirement id
url_req1 = 'http://eu-de.services.cloud.techzone.ibm.com:41967/grc/api/contents' + '/' + str(requirement_id_1)
url_req2 = 'http://eu-de.services.cloud.techzone.ibm.com:41967/grc/api/contents' + '/' + str(requirement_id_2)

# Set username and password
username = openpagesconfig.username
password = openpagesconfig.password

# Set authentication headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Set request method and data (in this case, it's a GET request with JSON data)
method = 'GET'

# Send the request
response1 = requests.request(method, url_req1, headers=headers, auth=(username, password))
response3 = requests.request(method, url_req2, headers=headers, auth=(username, password))

# Check if the response was successful (200 OK)
if response1.status_code == 200:
    print('Request successful!')
    print("Response1: ", response1.text)
    print("Response3: ", response3.text)

else:
    print("Response: ", response1.text)
    print(f'Request failed with status code {response1.status_code}')

# %% [markdown]
# ### Clean the content to plain text 

# %%
# Parse the JSON data
def parse_data(input_data):
    # Parse the JSON data
    data = input_data

    # Retrieve the value where "name": "OVIDE-Shared:Content"
    ovide_content_value = None
    for field in data['fields']['field']:
        if field['name'] == 'OVIDE-Shared:Content':
            ovide_content_value = field.get('value')
            break

    # Parse the HTML
    soup = BeautifulSoup(ovide_content_value, 'html.parser')

    # Find all hyperlinks
    hyperlinks = soup.find_all('a')

    # Count the number of hyperlinks
    num_hyperlinks = len(hyperlinks)

    plain_text = ''
    if ovide_content_value:
        soup = BeautifulSoup(ovide_content_value, 'html.parser')
        plain_text = soup.get_text()

    return ovide_content_value, num_hyperlinks, plain_text

data1 = json.loads(response1.text)
data3 = json.loads(response3.text)

ovide_content_value1, num_hyperlinks1, plain_text1 = parse_data(data1)
ovide_content_value3, num_hyperlinks3, plain_text3 = parse_data(data3)

print("Cleaned content for requirement1: ", plain_text1)
print("Cleaned content for requirement3: ", plain_text3)

# %% [markdown]
# ### Linking the articles

# %%
def modify_text(text, token, article_id):
    # Find the index of the given article ID in the text
    index_article = text.find(token)
    
    # Check if the article ID is found in the text
    if index_article != -1:
        # Construct the URL link based on the article ID
        url_link = "http://eu-de.services.cloud.techzone.ibm.com:41967/openpages/app/jspview/react/grc/task-view/" + str(article_id)
        
        # Construct the modified string with the <a> tag and the url_link
        modified_string = text[:index_article] + '<a href=\"' + url_link + '\">' + text[index_article:index_article+len(article_id)+3] + '</a>' + text[index_article+len(article_id)+3:]
        
        return modified_string
    else:
        return "Article not found in the text."


modified_string1 = modify_text(plain_text1, "article 3", requirement_id_2)
modified_string3 = modify_text(plain_text3, "article 1", requirement_id_1)

print(modified_string1)
print(modified_string3)

# %% [markdown]
# ### Update the GRC object

# %%
def update_json_data(text, id, name, reqid):
    # Set API endpoint URL
    url = 'http://eu-de.services.cloud.techzone.ibm.com:41967/grc/api/contents' + '/' + str(reqid)

    # Set username and password
    username = openpagesconfig.username
    password = openpagesconfig.password

    # Set authentication headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Set request method and data (in this case, it's a PUT request with JSON data)
    method = 'PUT'

    # Define the JSON data
    json_data = {
      "fields": {
        "field": [
          {
                "id": "7037",
                "dataType": "MEDIUM_STRING_TYPE",
                "name": "OVIDE-Shared:Content",
                "value": ""
            },
            {
                "id": "7034",
                "dataType": "ENUM_TYPE",
                "name": "OVIDE-Shared:Content HREF",
                "enumValue": {
                        "name": "Yes"
                 }
            },
            {
                "id": "7036",
                "dataType": "ENUM_TYPE",
                "name": "OVIDE-Shared:IntegrationStatus",
                "enumValue": {
                        "name": ""
                 }
            },
            {
                "id": "7035",
                "dataType": "INTEGER_TYPE",
                "name": "OVIDE-Shared:NB HREF",
                "value": "1"
            }
        ]
      },
      "typeDefinitionId": "79",
      "parentFolderId": "41872",
      "primaryParentId": "",
      "name": "",
      "description": "Represents a collection of controls with which an organization must comply"
    }

    # Update the value of "primaryParentID" and "name"
    json_data["primaryParentId"] = id
    json_data["name"] = name
    json_data['fields']['field'][0]['value'] = text
    souplen = BeautifulSoup(text, 'html.parser')
    hyperlinks = souplen.find_all('a')
    num_hyperlinks = len(hyperlinks)
    json_data['fields']['field'][3]['value'] = str(num_hyperlinks)
    json_data['fields']['field'][2]['enumValue']['name'] = "Cleaned"

    response = requests.request(method, url, headers=headers, json=json_data, auth=(username, password))

    if response.status_code == 200:
        print('Request successful!')
        print("Response: ", response.text)

    else:
        print("Response: ", response.text)
        print(f'Request failed with status code {response.status_code}')


update_json_data(modified_string1, Submandate_id, requirement_name_1, requirement_id_1)
update_json_data(modified_string3, Submandate_id, requirement_name_2, requirement_id_2)



# %%


# %%



