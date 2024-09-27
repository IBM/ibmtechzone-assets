import requests
import json
import os
import io
import base64
from PIL import Image
from urllib.parse import urlparse
from IPython.display import Image as DisplayImage, display  # Import display explicitly
from dotenv import load_dotenv

class WatsonXClient:
    def __init__(self, api_key, project_id, ibm_url):
        self.api_key = api_key
        self.project_id = project_id
        self.ibm_url = ibm_url
        self.token = self.get_watsonx_token()

    def get_watsonx_token(self):
        url = "https://iam.cloud.ibm.com/identity/token"
        payload = 'grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey&apikey=' + self.api_key
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            raise Exception(f"Error fetching token: {response.text}")
        return json.loads(response.text)['access_token']

    def is_url(self, string):
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def is_local_path(self, string):
        return os.path.exists(string)

    def encode_image_base64_from_localpath(self, image_path):
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_encoded = base64.b64encode(image_data).decode('utf-8')
        return base64_encoded

    def encode_image_base64_from_url(self, image_url: str) -> str:
        with requests.get(image_url) as response:
            response.raise_for_status()
            return base64.b64encode(response.content).decode('utf-8')

    def resize_base64_image(self, base64_string, size=(100, 100)):
        img_data = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_data))
        resized_img = img.resize(size, Image.LANCZOS)
        buffered = io.BytesIO()
        resized_img.save(buffered, format=img.format)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def read_image(self, user_image_input):
        if self.is_url(user_image_input):
            base64_image = self.encode_image_base64_from_url(user_image_input)
        elif self.is_local_path(user_image_input):
            base64_image = self.encode_image_base64_from_localpath(user_image_input)
        return self.resize_base64_image(base64_image)

    def display_image(self, user_image_input):
        if self.is_url(user_image_input):
            display(DisplayImage(url=user_image_input))
        elif self.is_local_path(user_image_input):
            display(DisplayImage(filename=user_image_input))

    def get_watsonx_response_llava(self, user_text_input, user_image_input):
        base64_image = self.read_image(user_image_input)
        
        lvlm_messages = [
            {
                "role": "system",
                "content": (
                    "You always answer the questions with markdown formatting using GitHub syntax. "
                    "The markdown formatting you support: headings, bold, italic, links, tables, lists, "
                    "code blocks, and blockquotes."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text_input},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64_image}}
                ]
            }
        ]

        body = {
            "messages": lvlm_messages,
            "project_id": self.project_id,
            "model_id": "meta-llama/llama3-llava-next-8b-hf",
            "decoding_method": "greedy",
            "repetition_penalty": 1,
            "max_tokens": 900
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token
        }

        response = requests.post(
            self.ibm_url,
            headers=headers,
            json=body
        )

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        data = response.json()
        return data['choices'][0]['message']['content']


# Example usage
if __name__ == "__main__":
    # Ask user for API key and project ID during runtime
    api_key = input("Enter your IBM Cloud API key: ")
    project_id = input("Enter your project ID: ")
    
    # Accept user input for text and image during runtime
    user_text_input = input("Enter the text input for the image description: ")
    user_image_input = input("Enter the image URL or local path for the image: ")

    # IBM URL remains constant for the WatsonX model
    ibm_url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"

    watsonx_client = WatsonXClient(api_key, project_id, ibm_url)
    result = watsonx_client.get_watsonx_response_llava(user_text_input, user_image_input)
    
    print(f"user_text_input: {user_text_input}")
    watsonx_client.display_image(user_image_input)
    print(f"Result: {result}")