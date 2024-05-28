# Author: Pinkal Patel
'''
Title: Text to Speech Conversion

Description:
This asset converts text to speech and saves it into a wav file. 

Environment:
wat_tts_key: # API KEY for Text to Speech Instance
wat_tts_url: # URL for text to Speech Instance


Requirements:
pip install ibm-watson==8.1.0;
pip install ibm_watson_machine_learning==1.0.357;
pip install python-dotenv==1.0.1
'''
from dotenv import load_dotenv
import os
import json
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.websocket import SynthesizeCallback

load_dotenv()
api_key = os.environ["wat_tts_key"]
url = os.environ["wat_tts_url"]
authenticator = IAMAuthenticator(api_key)
text_to_speech = TextToSpeechV1(authenticator=authenticator)
text_to_speech.set_service_url(url)

# get details for different voice
#voices = text_to_speech.list_voices().get_result()
#print(json.dumps(voices, indent=2))

# get details for different voice model
# voice_models = text_to_speech.list_custom_models().get_result()
# print(json.dumps(voice_models, indent=2))

file_path = "output.wav"
class MySynthesizeCallback(SynthesizeCallback):
    def __init__(self):
        SynthesizeCallback.__init__(self)
        self.fd = open(file_path, 'ab')

    def on_connected(self):
        print('Connection was successful')

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_content_type(self, content_type):
        print('Content type: {}'.format(content_type))

    def on_timing_information(self, timing_information):
        print(timing_information)

    def on_audio_stream(self, audio_stream):
        self.fd.write(audio_stream)

    def on_close(self):
        self.fd.close()
        print('Done synthesizing. Closing the connection')

my_callback = MySynthesizeCallback()

transcript = '''
thunderstorms could produce large hail isolated tornadoes and heavy rain
'''

text_to_speech.synthesize_using_websocket(transcript,
                                   my_callback,
                                   accept='audio/wav',
                                   voice='en-US_AllisonVoice'
                                  )