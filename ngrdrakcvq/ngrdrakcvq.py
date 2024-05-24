from transformers import AutoTokenizer
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route('/token_count', methods=['POST'])
def token_count():
    text = request.json.get('text', None)
    model_id = request.json.get('model_id', None)
    hf_token = request.json.get('hf_token', None)
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
    tokens = tokenizer.tokenize(text)
    num_tokens = len(tokens)
    return jsonify({"token_count":num_tokens})

if __name__== '__main__':
    
    app.run(debug=True)
