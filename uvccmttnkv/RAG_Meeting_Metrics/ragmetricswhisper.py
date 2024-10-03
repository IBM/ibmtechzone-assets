from fastapi import FastAPI, File, UploadFile, HTTPException
from pydub import AudioSegment
import os
import whisper
import configparser
import json
from ibm_watson_machine_learning.foundation_models import Model
import nltk
from nltk.translate.bleu_score import sentence_bleu
from rouge import Rouge
import pytrec_eval
from collections import defaultdict

# Download NLTK resources
nltk.download('punkt')
nltk.download('punkt_tab')
# Initialize FastAPI app
app = FastAPI()

# Initialize Whisper model for transcription
model = whisper.load_model("base")

# Directories to save uploaded audio files and transcribed text
AUDIO_SAVE_DIR = input("Enter directory name to save uplodaded audio files")
TRANSCRIBE_SAVE_DIR = input("Enter directory to save transcribed text")

# Ensure directories exist
os.makedirs(AUDIO_SAVE_DIR, exist_ok=True)
os.makedirs(TRANSCRIBE_SAVE_DIR, exist_ok=True)

# Variable to store transcribed text globally (in memory)
transcribed_text_global = {}

# Load WML credentials from config file
def get_wml_creds(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    api_key = config.get('credentials', 'api_key')
    ibm_cloud_url = config.get('credentials', 'ibm_cloud_url')
    project_id = config.get('credentials', 'project_id')
    
    if not api_key or not ibm_cloud_url or not project_id:
        raise ValueError("Ensure all required fields are present in the config file.")
    
    creds = {
        "url": ibm_cloud_url,
        "apikey": api_key
    }
    return project_id, creds

def ignore_trailing(input_string, keyword):
    index = input_string.find(keyword)
    if index != -1:
        return input_string[:index]
    else:
        return input_string

project_id, creds = get_wml_creds(".config")

# Transcription function
def transcribe_audio_to_text(file_path: str) -> str:
    # Load and convert the audio file
    audio = AudioSegment.from_file(file_path)
    
    # Export the audio to wav format
    wav_path = file_path.rsplit('.', 1)[0] + ".wav"
    audio.export(wav_path, format="wav")
    
    # Transcribe the audio using Whisper
    result = model.transcribe(wav_path)
    
    # Optionally delete the temporary wav file
    os.remove(wav_path)
    
    return str(result["text"].strip())

def beautify(text: str, query: str) -> str:
    model_id = "meta-llama/llama-3-2-70b-instruct"
    prompt_input = f"""<|start_header_id|>system<|end_header_id|>

You are an AI assistant trained to analyze meeting transcripts. Your task is to accurately answer any questions posed by the user based on the content
of the provided transcript. The transcript may include various details such as discussions, decisions, action items, attendees names and notes from 
the meeting. Include as much information from the transcript as possible related to the query, including people involved, any numbers, estimates and
dates if it is relevant to the query. If the names of the people are specified, keep a track of the people and display when asked and during minutes of the meeting. 
Do not start answer with "This transcript "

### Input:
- **Meeting Transcript:** {text}

### Instructions: If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. 
If you don't know the answer to a question, please don't share false information."""
    
    formattedQuestion = f"""<|begin_of_text|><|eot_id|><|start_header_id|>user<|end_header_id|>

    {query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
    
    prompt = f"{prompt_input}{formattedQuestion}"
    
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 2500,
        "min_new_tokens": 100,
        "repetition_penalty": 1,
        "stop_sequences": ["/n", "The information provided does not contain data for ", "Output: "]
    }

    model = Model(
        model_id=model_id,
        params=parameters,
        credentials=creds,
        project_id=project_id
    )
    
    generated_response = model.generate_text(prompt=prompt)
    generated_response = ignore_trailing(generated_response, 'Please ')
    generated_response = ignore_trailing(generated_response, 'Let me know ')
    generated_response = generated_response.replace("\n\n", " ").replace("\n\t", " ")

    return generated_response 

# Metric calculation for RAG
def calculate_metrics(reference_text: str, generated_text: str, relevant_docs: int = 1):
    # Generation Metrics
    bleu_score = sentence_bleu([nltk.word_tokenize(reference_text)], nltk.word_tokenize(generated_text))
    
    rouge = Rouge()
    rouge_scores = rouge.get_scores(generated_text, reference_text, avg=True)
    
    # Retrieval Metrics (simulated, as no actual retrieval is done here)
    retrieval_results = {  # Mock retrieval results (ranked list of documents)
        '1': {'relevance': 1},
        '2': {'relevance': 0}
    }
    qrels = {
        '1': {'1': 1}
    }

    # Precision@k, Recall@k, MRR, nDCG
    evaluator = pytrec_eval.RelevanceEvaluator(qrels, pytrec_eval.supported_measures)
    evaluation = evaluator.evaluate(retrieval_results)
    
    metrics = {
        "bleu_score": bleu_score,
        "rouge_1": rouge_scores['rouge-1']['f'],
        "rouge_2": rouge_scores['rouge-2']['f'],
        "rouge_l": rouge_scores['rouge-l']['f'],
        "precision_at_k": evaluation['1']['P_1'],
        "recall_at_k": evaluation['1']['recall_1'],
        "mrr": evaluation['1']['recip_rank'],
        "ndcg": evaluation['1']['ndcg']
    }
    
    return metrics

# FastAPI route to upload and transcribe audio
@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename.endswith(('.mp3', '.wav', '.ogg', '.mp4')):
        raise HTTPException(status_code=400, detail="File format not supported.")
    
    # Save the file in the audio directory
    file_path = os.path.join(AUDIO_SAVE_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Transcribe the audio file to text
    transcribed_text = transcribe_audio_to_text(file_path)
    
    # Save transcribed text to a file
    transcribed_text_file_path = os.path.join(TRANSCRIBE_SAVE_DIR, f"{file.filename}.txt")
    with open(transcribed_text_file_path, "w") as f:
        f.write(transcribed_text)
    
    # Store the transcribed text globally (in memory)
    transcribed_text_global['text'] = transcribed_text
    
    return {"message": "File uploaded and transcribed successfully", "transcription": transcribed_text}

# FastAPI route to perform RAG, beautify the text, and compute metrics
@app.post("/rag/")
async def rag_endpoint(query: str):
    # Get the latest transcribed text file from the paperrag directory
    text_files = os.listdir(TRANSCRIBE_SAVE_DIR)
    if not text_files:
        raise HTTPException(status_code=404, detail="No transcribed text available. Please upload and transcribe audio first.")
    
    # Assuming you want to read the most recently added text file
    latest_file = max([os.path.join(TRANSCRIBE_SAVE_DIR, f) for f in text_files], key=os.path.getctime)

    with open(latest_file, "r") as f:
        transcribed_text = f.read()
    
    # Beautify the transcribed text based on the query
    beautified_text = beautify(transcribed_text, query)
    
    # For metrics calculation, assume the reference text is the same as transcribed text (for demonstration purposes)
    metrics = calculate_metrics(transcribed_text, beautified_text)
    
    return {"response": beautified_text, "metrics": metrics}
