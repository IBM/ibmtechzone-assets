from flask import Flask, request, Response
import requests
import argparse
import time
import json

# Initialize Flask app
app = Flask(__name__)

# Command-line arguments
parser = argparse.ArgumentParser(description="Proxy API between Watsonx and OpenAI")
parser.add_argument('--project_id', default=None, help='Watsonx Project ID (Optional)')
parser.add_argument('--bearer_token', required=True, help='Watsonx Bearer Token')
parser.add_argument('--api_url', default='https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2023-05-29', help='watsonx/bam API URL')
parser.add_argument('--api_type', required=True, choices=['watsonx', 'bam'], help='API type: watsonx or bam')
args = parser.parse_args()


def transform_to_llama2_input(messages):

    if messages[0]['role'] == "system":
        message_str = "".join([f" <<SYS>>{messages[0]['content']}<</SYS>>\n"]+[f"\n{msg['role']}: {msg['content']}\n" for msg in messages[1:]])
    else :
        message_str = "".join([f"{msg['role']}: {msg['content']}\n" for msg in messages])
    input_str = f"<s>[INST]{message_str.rstrip()}[/INST]\n"
    return input_str



@app.route("/v1/chat/completions", methods=['POST'])
def proxy():
    # Extract payload from OpenAI-compatible API request
    openai_payload = request.json

    messages = openai_payload["messages"]
    MODEL_ID = openai_payload["model"]
    # Discriminate between Watsonx and BAM
    if args.api_type == 'watsonx':
        llama2_input = transform_to_llama2_input(messages)
        watsonx_payload = {
            "model_id": f"{MODEL_ID}",
            "input": llama2_input,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 1000,
                "min_new_tokens": 0,
                "stop_sequences": ["user:"],
                "temperature": 0.7,
                "top_k": 50,
                "top_p": 1,
                "repetition_penalty": 1
            },
            "project_id": args.project_id if args.project_id else None
        }
        # Make request to Watsonx API
        response = requests.post(
            f"{args.api_url}",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {args.bearer_token}'
            },
            json=watsonx_payload
        )
    elif args.api_type == 'bam':
        bam_input = transform_to_llama2_input(messages)
        bam_payload = {
            "model_id":  f"{MODEL_ID}",
            "input": bam_input,
            "parameters": {
                "decoding_method": "greedy",
                "min_new_tokens": 1,
                "max_new_tokens": 2000,
                "temperature": 0.7,
                

            }
        }
      
        #print("bam_payload: ",bam_payload)
        # Make request to BAM API (replace with the actual BAM URL)
        response = requests.post(
            f"{args.api_url}?version=2024-04-15",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {args.bearer_token}'
            },
            json=bam_payload
        )
        


    # Convert Watsonx response to OpenAI-compatible response
    watsonx_output = response.json()
    results = watsonx_output.get("results", [{}])
    content = results[0].get("generated_text", "") if results else ""
    
    # print("############# RESULT #################")
    # print("RESULT: ",watsonx_output)
    # print("########################################")
    stream = openai_payload.get("stream", False)

    # Determine the response format based on the "stream" field
    if stream:
        response_format = {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": f"gpt-{MODEL_ID}",
            "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": "stop"}]
        }
    else:
        response_format = {
            "id": "chatcmpl-abc123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": f"gpt-{MODEL_ID}",
            "usage": {
                "prompt_tokens": results[0].get("input_token_count", 0) if results else 0,
                "completion_tokens": results[0].get("generated_token_count", 0) if results else 0,
                "total_tokens": results[0].get("input_token_count", 0) + results[0].get("generated_token_count", 0) if results else 0
            },
            "choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": results[0].get("stop_reason", "stop") if results else "stop", "index": 0}]
        }


    return Response(json.dumps(response_format), content_type='application/json'), 200

if __name__ == "__main__":
    app.run(debug=True, port=5432)