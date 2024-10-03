
# RAGMetricsWhisper FastAPI Service

This project is a FastAPI service that transcribes audio files into text using OpenAI's Whisper model, beautifies the transcribed text using a LLaMA model, and computes various metrics for the generated text.

## Features

- Upload and transcribe audio files in various formats (mp3, wav, ogg, mp4)
- Generate a beautified response from the transcription based on a given query using a LLaMA model
- Calculate evaluation metrics for the transcription and generation process, including BLEU, ROUGE, Precision@k, Recall@k, Mean Reciprocal Rank (MRR), and Normalized Discounted Cumulative Gain (nDCG)

## Setup Instructions

### Step 1: Install Dependencies
Ensure you have Python 3.8 or higher installed, and then install the required dependencies:

```bash
pip install fastapi pydub whisper nltk rouge pytrec_eval ibm_watson_machine_learning uvicorn
```

### Step 2: Download NLTK Resources
The application requires NLTK resources for BLEU score computation. Run the following commands:

```python
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
```

### Step 3: Create Config File
Create a `.config` file in the root directory with the following format:

```ini
[credentials]
api_key=<your_ibm_wml_api_key>
ibm_cloud_url=<your_ibm_cloud_url>
project_id=<your_project_id>
```

### Step 4: Run the Application
You can run the FastAPI application using the following command:

```bash
uvicorn ragmetricswhisper:app --reload
```

### Step 5: Upload and Transcribe Audio
You can upload an audio file using the `/upload-audio/` endpoint. Supported formats include `.mp3`, `.wav`, `.ogg`, and `.mp4`.

### Step 6: Perform RAG and Retrieve Metrics
After transcribing an audio file, you can send a query to the `/rag/` endpoint, which will return a beautified response and evaluation metrics.

## Endpoints

### POST `/upload-audio/`
Upload an audio file and transcribe it.

- **Request**: Form-data, file upload
- **Response**: JSON containing the transcription

### POST `/rag/`
Perform retrieval-augmented generation (RAG) based on the latest transcription and return evaluation metrics.

- **Request**: JSON containing the query string
- **Response**: JSON containing the beautified response and the evaluation metrics

## License
This project is licensed under the MIT License.
