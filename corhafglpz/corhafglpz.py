import time, os, io
import librosa
import pandas as pd
import soundfile as sf
from typing import Dict, Optional
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1

from dotenv import load_dotenv
load_dotenv()

API_KEY=os.getenv("api_key")
URL=os.getenv("url")
MODEL=os.getenv("model")

class WatsonSTTParser:
    def __init__(self):
        self._config = {
            "API_KEY": API_KEY,
            "URL": URL,
            "MODEL": MODEL,
            "CONTENT_TYPE": "audio/wav"
        }
        self._authenticator =  IAMAuthenticator(self._config['API_KEY'])
        self._speech_to_text = SpeechToTextV1(authenticator = self._authenticator)
        self._speech_to_text.set_service_url(self._config['URL'])
        self._speech_to_text.set_disable_ssl_verification(True)

    def transcribe(self, audio_file: str) -> Dict:
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"{audio_file} do not exists.")

        with open(audio_file, 'rb') as file:
            speech_recognition_results = self._speech_to_text.recognize(
                audio=file,
                model=self._config['MODEL'],
                language_customization_id= self._config['CUSTOM_ID'],
                content_type=self._config['CONTENT_TYPE'],
                speaker_labels=True
            ).get_result()
        return speech_recognition_results
    
    def async_transcribe(self, audio_file):
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"{audio_file} do not exists.")

        with open(audio_file, 'rb') as file:
            recognition_job = self._speech_to_text.create_job(
                audio=file,
                model=self._config['MODEL'],
                language_customization_id= self._config['CUSTOM_ID'],
                content_type=self._config['CONTENT_TYPE'],
                speaker_labels=True
            ).get_result()
        return recognition_job
    
    def async_transcribe_multi_channel(self, audio_file):
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"{audio_file} do not exists.")
        y, sr = librosa.load(audio_file, sr=None, mono=False)
        num_channels = y.shape[0] if len(y.shape) > 1 else 1
        if num_channels==1:
            y = y.reshape(1,-1)
        output = {}
        for channel in range(num_channels):
            temp_file = io.BytesIO()
            sf.write(temp_file, y[channel, :], sr, format="wav")
            temp_file.seek(0)
            recognition_job = self._speech_to_text.create_job(
                audio=temp_file,
                model=self._config['MODEL'],
                language_customization_id= self._config['CUSTOM_ID'],
                content_type=self._config['CONTENT_TYPE'],
                speaker_labels=True
            ).get_result()
            output[f'channel_{channel}'] = recognition_job['id']
        return output
        
    
    def check_all_jobs(self):
        recognition_jobs = self._speech_to_text.check_jobs().get_result()
        job_status = {}
        if 'recognitions' in recognition_jobs:
            recognitions = recognition_jobs['recognitions']
            for job in recognitions:
                job_status[job['id']] = job['status']
        return job_status
    
    def check_all_jobs_completed(self, ids, job_status):
        for id in ids:
            if job_status[id] not in ['completed', 'failed']:
                return False
        return True
    
    def get_job_result(self, id):
        speech_recognition_result = self._speech_to_text.check_job(id).get_result()
        if speech_recognition_result['status'] not in ['completed', 'failed']:
            time.sleep(3)
            speech_recognition_result = self._speech_to_text.check_job(id).get_result()
        return speech_recognition_result
    
    def parse_transcription(self, results):
        labels = pd.DataFrame.from_records(results['speaker_labels'])
        transcript_tstamps = pd.DataFrame.from_records(
            [t for r in results['results']
                for a in r['alternatives']
                for t in a['timestamps']],
            columns=['word', 'from', 'to']
        )

        df = labels.merge(transcript_tstamps)
        df = df.sort_values(['from', 'to'])
        df['current_speaker'] = (df.speaker.shift() != df.speaker).cumsum()

        transcripts = df.groupby('current_speaker').agg({
            'speaker': "min",
            'word': lambda x: ' '.join(x),
            'from': "min",
            'to': "max"
        }).rename(columns={'word': 'transcript'})

        transcripts['speaker'] = "Speaker " + transcripts['speaker'].astype(str) + ":"
        transcripts["full sentence"] = transcripts["speaker"] + " " + transcripts["transcript"]
        transcript = "\n".join(transcripts["full sentence"].astype(str))

        return transcript