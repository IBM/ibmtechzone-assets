import os
import json
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1 , TextToSpeechV1
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from genai.schema import TextGenerationParameters, TextGenerationReturnOptions
from genai import Credentials, Client
from genai.extensions.langchain import LangChainInterface
import subprocess
subprocess.run(['wget', '-O', 'sample.mp4', 'https://drive.google.com/uc?export=download&id=17i-vQn0r_m59q37Jsn35jFRJXg3yX8nX'], check=True)



API_KEY_STT = os.environ["api_key_stt"]
URL_STT = os.environ["url_stt"]
API_KEY_TTS = os.environ["api_key_tts"]
URL_TTS = os.environ["url_tts"]
BAM_API_KEY = os.environ["bam_api_key"]
BAM_API_ENDPOINT = os.environ["bam_api_endpoint"]



SOURCE_LANGUAGE = "English"
TARGET_LANGUAGE = "Spanish"    
INPUT_MP4_FILE_PATH = "sample.mp4"
FILENAME = os.path.splitext(INPUT_MP4_FILE_PATH)[0] 
AUDIO_OUTPUT_PATH = FILENAME + ".wav"
MERGED_OUTPUT_PATH = "output_" + FILENAME + ".mp4"



TRANSLATION_PROMPT = '''[INST] <<SYS>> As an expert Translator, your task is to perform literal translation of the given text from {source} language to {target} language. <</SYS>>
Consider the below points while translating:
- You are a {target} Professor who's proficient in {source} to {target} translation.
- You are able to convey the exact intent as the input without adding additional jargon in the translation.
- Preserve the exact meaning of the original {source} input text in the translated {target} text.
- Generate response only using {target} characters. Do not make any spelling mistakes in {target} while translation.
- Only perform the translation without adding any additional words.
- Provide the correct translated text in the specified JSON format with translated_text as Key. Do not include any explanation or additional text in the response. Just provide the translated text in {target} language in the specified JSON format with translated_text as Key. 
Output:
{{
    "translated_text": "..."
}}

Input Text:
{text}

[/INST]
'''



class MySpeechToText:
    def __init__(self):
        self.authenticator = IAMAuthenticator(API_KEY_STT)
        self.stt_client = SpeechToTextV1(authenticator = self.authenticator)
        self.stt_client.set_service_url(URL_STT)
        print("Authentication and STT Client Setup Done!") 

    def calculate_total_duration(self, audio):
        total_duration = len(audio)
        duration_in_seconds = total_duration / 1000            # Convert milliseconds to seconds
        hours = int(duration_in_seconds // 3600)
        minutes = int((duration_in_seconds % 3600) // 60)
        seconds = int(duration_in_seconds % 60)
        duration_formatted = f"{hours}:{minutes:02d}:{seconds:02d}"  # Format hours, minutes, seconds
        return total_duration, duration_formatted

    def recognize(self, audio_path, segment_duration = 120 * 1000, STT_MODEL_NAME = 'en-US_BroadbandModel'):
        audio = AudioSegment.from_file(audio_path)
        total_duration, duration_formatted = self.calculate_total_duration(audio)
        print("Audio Duration:", duration_formatted)
        print(f"Getting STT results for {audio_path}")
        combined_transcript = ''
        for start_time in range(0, total_duration, segment_duration):
            end_time = min(start_time + segment_duration, total_duration)
            segment = audio[start_time:end_time]
            with segment.export(format="wav") as wav_file:
                speech_recognition_results = self.stt_client.recognize(audio=wav_file.read(), content_type='audio/wav', model=STT_MODEL_NAME).get_result()        
            for result in speech_recognition_results['results']:
                transcript = result['alternatives'][0]['transcript'].strip()
                combined_transcript += transcript + '. '
        print(f"Obtained Transcript: {combined_transcript.strip()}")
        return combined_transcript.strip()
    


class watsonxTranslator:
    def __init__(self):
        self.creds = Credentials(api_key = BAM_API_KEY, api_endpoint = BAM_API_ENDPOINT)
        self.client = Client(credentials = self.creds)
        self.source_language = SOURCE_LANGUAGE
        self.target_language = TARGET_LANGUAGE
        print("Authentication and watsonx.ai Client Setup Done!")

    def translate(self, input_text):
        translation_prompt = self._get_translation_prompt(input_text)
        response = list(self.client.text.generation.create(model_id="mistralai/mixtral-8x7b-instruct-v01", inputs=translation_prompt, 
                                                       parameters=TextGenerationParameters(max_new_tokens=2500, min_new_tokens=1, decoding_method="greedy", stop_sequences=["</s>"])))
        result = response[0].results[0].generated_text
        try:
            translated_text = json.loads(result, strict=False).get('translated_text', '').strip()
        except:
            translated_text = json.loads(result + '"\n}').get('translated_text', '').strip()
        print("Translated Text:" , translated_text)
        return translated_text

    def _get_translation_prompt(self, input_text):
        return TRANSLATION_PROMPT.format(
            source=self.source_language,
            target=self.target_language,
            text=input_text
        )



class MyTextToSpeech:
    def __init__(self):
        self.authenticator = IAMAuthenticator(API_KEY_TTS)
        self.tts_client = TextToSpeechV1(authenticator = self.authenticator)
        self.tts_client.set_service_url(URL_TTS)
        print("Authentication and TTS Client Setup Done!")
    
    def synthesize_audio(self, text, output_file, format = 'audio/wav', TTS_VOICE = 'es-ES_EnriqueV3Voice'):
        print("Started synthesizing audio for obtained translation....")
        with open(output_file, 'wb') as audio_file:
            audio_file.write(self.tts_client.synthesize(text = text, voice = TTS_VOICE, accept = format).get_result().content)
        print(f"Obtained audio synthesized to {output_file}")



stt_client = MySpeechToText()
wx_translator = watsonxTranslator()
tts_client = MyTextToSpeech()

output_text = stt_client.recognize(INPUT_MP4_FILE_PATH)
translated_text = wx_translator.translate(output_text)
tts_client.synthesize_audio(translated_text, output_file=AUDIO_OUTPUT_PATH)

video_clip = VideoFileClip(INPUT_MP4_FILE_PATH)
audio_clip = AudioFileClip(AUDIO_OUTPUT_PATH)

final_clip = video_clip.set_audio(audio_clip)
final_clip.write_videofile(MERGED_OUTPUT_PATH)