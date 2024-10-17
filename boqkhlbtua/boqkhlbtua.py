# NOTE: You would be expected to generate a new bearer token because it expires every hour
import base64
from PIL import Image
import requests
import subprocess

def augment_api_request_body(user_query, image):
    body = {
            "messages": [{"role":"user","content":[{"type":"text","text":user_query},
                         {"type":"image_url","image_url":{"url": f"data:image/jpeg;base64,{image}"}}]}],
            "project_id": credentials.get("project_id"),
            "model_id": "meta-llama/llama-3-2-90b-vision-instruct",
            "decoding_method": "greedy",
            "repetition_penalty": 1,
            "max_tokens": 500
        }
    return body

def run_command(api_key):
    try:
        command = f'''
            curl -fsSL https://clis.cloud.ibm.com/install/osx | sh
            ibmcloud login --apikey {api_key}
            ibmcloud iam oauth-tokens
            ''' 
        # Run the command
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Fetch the output
        output = result.stdout.strip()
        index = output.index('Bearer')
        return output[index:]
    except subprocess.CalledProcessError as e:
        # Handle errors (if the command fails)
        print(f"Error executing command: {e.stderr}")
        return None

bearer_token = run_command('API_KEY')
if bearer_token:
    print(f"Command Output:\n{bearer_token}")

credentials = {
    "url": "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29",
    "project_id": "PROJECT_ID",
    "api_key": "API_KEY",
    "bearer_token": f"{bearer_token}"
}

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": credentials.get("bearer_token")
}

system_prompt = '''You are a very helpful assisstant Always answer as helpfully as possible, while being safe. 
You Always answer as helpfully as possible, while being safe.

Instructions:
1. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content.
2. Be concise in your answer
3. Be socially unbiased and positive in nature.
4. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. 
5. If you don't know the answer to a question, please don't share false information. Please produce concise responses.
'''

# Image path of local file
encoded_images = []
with open("image.png", "rb") as image_file:
    encoded_images.append(base64.b64encode(image_file.read()).decode("utf-8"))

for i in range(len(encoded_images)):
    image = encoded_images[i]
    user_query = "Describe the image for me please."
    request_body = augment_api_request_body(user_query, image)
    response = requests.post(
        credentials.get("url"),
        headers=headers,
        json=request_body
        )
    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))
    
    data = response.json()
    print(data['choices'][0]['message']['content'])