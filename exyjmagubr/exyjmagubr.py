from flask import Flask, request, jsonify
from langdetect import detect

app = Flask(__name__)


def detect_language(text):
    try:
        lang = detect(text)
        return lang
    except:
        return "unknown"


@app.route("/detect_language", methods=["POST"])
def detect_language_endpoint():
    data = request.get_json()
    text = data.get("text", "")
    language = detect_language(text)
    return jsonify({"language": language})


if __name__ == "__main__":
    app.run(debug=True)
