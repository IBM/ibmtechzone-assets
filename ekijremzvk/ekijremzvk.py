from flask import Flask, jsonify, request
import boto3
import os
from dotenv import load_dotenv

app = Flask(__name__)
#CORS(app)

# load environment variable from .env file
load_dotenv()

service_endpoint=os.environ["cos_service_endpoint"]
cos_access_key_id=os.environ["cos_access_key"]
cos_secret_access_key=os.environ["cos_secret_key"]

cos_client = boto3.client('s3',
                          endpoint_url = service_endpoint,
                          aws_access_key_id=cos_access_key_id,
                          aws_secret_access_key=cos_secret_access_key)

print("service endpoint: ", service_endpoint)
print("cos access key: ", cos_access_key_id)

# Return all buckets in your COS instance
def get_all_buckets(cos_client):
    response = cos_client.list_buckets()
    allbuckets = []
    for bucket in response['Buckets']:
        allbuckets.append(bucket['Name'])
    return allbuckets

@app.route('/buckets')
def get_buckets():
    # List all buckets in your COS instance
    buckets = get_all_buckets(cos_client)
    return jsonify(buckets)


@app.route("/")
def home():
    return "Hello, Flask!"

# main driver function
if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()