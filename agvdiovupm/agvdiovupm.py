import requests
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("api_key", None)
collection_id = os.getenv("collection_id", None)
url = f"https://api.getpostman.com/collections/{collection_id}/transformations"

headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key
}

response = requests.get(url, headers=headers)

# Check for successful response
if response.status_code == 200:
  # Assuming the response is JSON, parse it
  data = response.json()
  # Access the 'output' key and print it
  output = data.get('output')
  print(output)
else:
  print(f"Error: API request failed with status code {response.status_code}")
