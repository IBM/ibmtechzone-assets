import os
os.chdir('/Users/prathampayra/Documents/Bank of columbia/Audios de prueba')

import whisper
import json
import os

# openAI part // do not do for this project

whisper_model = whisper.load_model("large-v2")

os.listdir('/Users/prathampayra/Documents/Bank of columbia/Audios de prueba')

result = whisper_model.transcribe("vys_01E4C4G430AN1F651C4H5B5AES0G0L5J_2024-01-03_04-23-28_0.mp3")


transcripts= []
for segment in result['segments']:
    transcripts.append({
        'Text' : segment['text'].strip(),
        'Start' : segment['start'],
        'End' : segment['end']
    })
transcripts