from flask import Flask, request, jsonify
from semantic_compare import similarity_score_calculator, highlight_similarity

app = Flask(__name__)

@app.route('/api/v1/semantic/compare', methods=['POST'])
def process_post_request():
    if request.method == 'POST':
        data = request.get_json()
        ground_truth = data['ground_truth']
        infer_value = data['infered_value']
        similarity_score = similarity_score_calculator(ground_truth,infer_value)
        return jsonify({'similarity_score': f'{similarity_score}',"ground truth":f'{ground_truth}',"infered value":f'{infer_value}'}), 201
    else:
        return jsonify({'message': 'Invalid request method'}), 400
    
@app.route('/api/v1/semantic/highlight', methods=['POST'])
def process_post_request_highlight():
    if request.method == 'POST':
        data = request.get_json()
        ground_truth = data['ground_truth']
        infer_value = data['infered_value']
        hightlights = highlight_similarity(ground_truth,infer_value)
        return jsonify({'hightlights': f'{hightlights}',"ground truth":f'{ground_truth}',"infered value":f'{infer_value}'}), 201
    else:
        return jsonify({'message': 'Invalid request method'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
