import requests
import json

STEPZEN_AUTH = os.environ["stepzen_auth"]
STEPZEN_URL = os.environ["stepzen_url"]
STEPZEN_QUERY = os.environ["stepzen_query"]

query = STEPZEN_QUERY
variables = {}

headers = {'Authorization': STEPZEN_AUTH}
url = STEPZEN_URL
r = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
data = r.json()
print(json.dumps(data, indent=2))