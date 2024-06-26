from PIL import Image
import pytesseract
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process_text', methods=['POST'])
def process_text():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400
    
    image_file = request.files['image']
    
    # Use pytesseract to extract text from the uploaded image
    text = pytesseract.image_to_string(Image.open(image_file.stream))
    
    # Process the extracted text as needed (e.g., remove punctuation, convert to lowercase)
    processed_text = text.lower().replace(',', '').replace('.', '')
    
    return jsonify({'processed_text': processed_text})

if __name__ == '__main__':
    app.run(debug=True)
