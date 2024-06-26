from flask import Flask, request, jsonify
from semantic_compare import similarity_score_calculator
from tagger_model import get_model_inference,get_model_inference_topic, get_model_inference_test_case
from classifier import get_class_response
import json

app = Flask(__name__)

    
@app.route('/api/v1/complex/classification', methods=['POST'])
def complex_classify():
    if request.method == 'POST':
        data = request.get_json()
        classified_list = get_model_inference(data['requirement'],data['option'])
        return jsonify({'classification': classified_list}), 201
    else:
        return jsonify({'message': 'Invalid request method'}), 400

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
