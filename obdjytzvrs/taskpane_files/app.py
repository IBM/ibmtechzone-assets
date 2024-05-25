from flask import Flask, request, jsonify
import ssl
from flask_cors import CORS
from genai.schema import TextGenerationParameters
from langchain_community.document_loaders import TextLoader
from genai import Credentials, Client

app = Flask(__name__)
CORS(app) 


# Define the path to the office-addin certificate and key files
certificate_path = '/root-directory/.office-addin-dev-certs/localhost.crt'
key_path = '/root-directory/.office-addin-dev-certs/localhost.key'


from dotenv import load_dotenv
load_dotenv()

## Mention your BAM Credentials
BAM_API_KEY = "YOUR_BAM_CREDENTIAL"
BAM_API_ENDPOINT = "YOUR_BAM_CREDENTIAL"

# credentials = Credentials.from_env()
credentials = Credentials(api_key=BAM_API_KEY, api_endpoint=BAM_API_ENDPOINT)
client = Client(credentials=credentials)

@app.route('/data', methods=['POST', 'PUT', 'OPTIONS'])
def receive_data():
    if request.method == 'OPTIONS':
        # Handle CORS preflight requests
        response = app.response_class(
            response="CORS preflight request successful",
            status=200
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    elif request.method in ['POST', 'PUT']:

        # # Handle CORS preflight requests
        response = app.response_class(
            response="CORS preflight request successful",
            status=200
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, PUT'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'


        data = request.get_json()
        # text = request.get_data(as_text=True)
        text = data.get('text')

        print (request)
        print (request.headers)
        print('Received data from Office Add-in:')

        # Further processing with the received data #####################

        ### converting str text data to .txt format(exp. with additional info)
        ### or we can directly feed data to the model
        def save_text_to_file(text, file_path):
            with open(file_path, 'w') as file:
                file.write(text)
        file_path = "output.txt"
        # Save text to .txt file
        save_text_to_file(text, file_path)
        print("Text saved to", file_path)

        loader = TextLoader(file_path)
        data_to_model = loader.load()

        summerization_prompt = " Your model prompt goes here: {text} "

        response = list(
            client.text.generation.create(
                model_id = "meta-llama/llama-3-70b-instruct",
                # inputs=[summerization_prompt.format(context=data_to_model)], ## with tokenized
                inputs=[summerization_prompt.format(context=text)],  ## raw text
                
                parameters=TextGenerationParameters(
                        decoding_method='greedy',
                        max_new_tokens=2048, #for llama 2
                        min_new_tokens=10,
                        temperature=0.05
                ),
            )
        )

        result = response[0].results[0]

        processed_data = result.generated_text
        return jsonify({'processed_text': processed_data})
    else:
        return 'Method not allowed', 405

if __name__ == '__main__':
    # Create SSL context using provided certificate and key
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=certificate_path, keyfile=key_path)
    # Run Flask app with SSL context
    app.run(debug=True, port=5004, ssl_context=ssl_context)




