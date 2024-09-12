import argparse
import base64
import configparser
import json
import threading
import time
from functools import partial

# import pyaudio
import websocket
from websocket._abnf import ABNF
import time
import queue
import os
from dotenv import load_dotenv

model = "ja-JP_Telephony_LSM"

# variable to check the close status of transcription
close_status_channel_1 = "No"
close_status_channel_2 = "No"


CHUNK = 1024

# Rate is important, nothing works without it. This is a pretty
# standard default. If you have an audio device that requires
# something different, change this.
RATE = 8000

# variables holding teh final transcription
FINALS_channel_1 = []
FINALS_channel_2 = []
LAST_channel_1 = None
LAST_channel_2 = None

# speech to text LSM model
model = "ja-JP_Telephony_LSM"

#an audio queue channel to hold the call audio data
audio_queue_channel1 = queue.Queue()
audio_queue_channel_2 = queue.Queue()

#catches the audio stream from the twilio and sends it to stream_channel 1 and 2 separetly
def stream(audio_data_channel1,audio_data_channel2):
    stream_channel1(audio_data_channel1)
    stream_channel2(audio_data_channel2)

#catches the audio from strem method and stores it in a audio queue
def stream_channel1(audio_data):
    global audio_queue_channel1
    audio_queue_channel1.put(audio_data)
    #print("audio in stream is:", audio_data)

def stream_channel2(audio_data):
    global audio_queue_channel_2
    audio_queue_channel_2.put(audio_data)
    #print("audio in stream is:", audio_data)

#catches the audio from stream method and stores it in a audio queue
def save_stream_channel_1():
    global audio_queue_channel1
    if not audio_queue_channel1.empty():
        audio = audio_queue_channel1.get()
        #print("audio in save_stream is:", audio)
        return audio
    return None

def save_stream_channel_2():
    global audio_queue_channel_2
    if not audio_queue_channel_2.empty():
        audio = audio_queue_channel_2.get()
        #print("audio in save_stream is:", audio)
        return audio
    return None

def read_audio_channel_1(ws):
    """Read audio and sent it to the websocket port."""

    global close_status_channel_1
    
    # the loop twilio call is not ended and is monitored by variale 'close_status_channel_1'
    while close_status_channel_1 == "No":
        audio = save_stream_channel_1()
        if audio:
            try:
                if ws.sock and ws.sock.connected:
                    for i in range(0, len(audio), CHUNK):
                        chunk = audio[i:i + CHUNK]
                        ws.send(chunk, ABNF.OPCODE_BINARY)
                    
                else:
                    print("WebSocket is not connected")
            except websocket.WebSocketConnectionClosedException as e:
                
                print("WebSocket connection closed:", e)

            except Exception as e:
                print("Error sending audio:", e)
        close_status_channel_1 = save_close_status_channel_1()

# please follow the comments for channel_1
def read_audio_channel_2(ws):
    """Read audio and sent it to the websocket port."""
    
    global close_status_channel_2
    
    while close_status_channel_2 == "No":
        audio = save_stream_channel_2()
        if audio:
            
            try:
                if ws.sock and ws.sock.connected:
                    for i in range(0, len(audio), CHUNK):
                        chunk = audio[i:i + CHUNK]
                        ws.send(chunk, ABNF.OPCODE_BINARY)
                else:
                    print("WebSocket is not connected")
            except websocket.WebSocketConnectionClosedException as e:
                
                print("WebSocket connection closed:", e)
            except Exception as e:
                print("Error sending audio:", e)
            
        close_status_channel_2 = save_close_status_channel_2()
    
# when twilio call gets cut , the variable is assigned the 'yes' value
def closeTranscriber_channel_1():
    global close_status_channel_1
    close_status_channel_1 = "yes"
    save_close_status_channel_1()

# when twilio call gets cut , the variable is assigned the 'yes' value
def closeTranscriber_channel_2():
    global close_status_channel_2
    close_status_channel_2 = "yes"
    save_close_status_channel_2()

# returns the close status variable 
def save_close_status_channel_1():
    global close_status_channel_1
    return close_status_channel_1
# returns the close status variable 

def save_close_status_channel_2():
    global close_status_channel_2
    return close_status_channel_2

# closes the websocket when the twilio call gets disconnected
def close_transcriber_channel_1(ws):
    global close_status_channel_1
    while True:
        close_status_channel_1 = save_close_status_channel_1()
        
        if close_status_channel_1 == "yes":
            data = {"action": "stop"}
            ws.send(json.dumps(data).encode('utf8'))
            # ... which we need to wait for before we shutdown the websocket
            time.sleep(0.001)
            ws.close()
            break

# closes the websocket when the twilio call gets disconnected
def close_transcriber_channel_2(ws):
    global close_status_channel_2
    
    while True:
        close_status_channel_2 = save_close_status_channel_2()
        if close_status_channel_2 == "yes":
            data = {"action": "stop"}
            ws.send(json.dumps(data).encode('utf8'))
            time.sleep(0.001)
            ws.close()
            break



def on_message_channel_1(self, msg):
    """Print whatever messages come in.

    While we are processing any non trivial stream of speech Watson
    will start chunking results into bits of transcripts that it
    considers "final", and start on a new stretch. It's not always
    clear why it does this. However, it means that as we are
    processing text, any time we see a final chunk, we need to save it
    off for later.
    """
    global LAST_channel_1
    data = json.loads(msg)
    if "results" in data:
        if data["results"][0]["final"]:
            FINALS_channel_1.append(data)
            LAST_channel_1 = None
        else:
            LAST_channel_1 = data
        # This prints out the current fragment that we are working on
        print("channel_1:",data['results'][0]['alternatives'][0]['transcript'])

        

def on_message_channel_2(self, msg):
    
    global LAST_channel_2
    data = json.loads(msg)

    if "results" in data:
        if data["results"][0]["final"]:
            FINALS_channel_2.append(data)
            LAST_channel_2 = None
        else:
            LAST_channel_2 = data
        # This prints out the current fragment that we are working on
        print("channel_2:",data['results'][0]['alternatives'][0]['transcript'])


# WEBSOCKET on error message
def on_error_channel_1(self, error):
    """Print any errors."""
    print("error is:",error)

# WEBSOCKET on error message
def on_error_channel_2(self, error):
    """Print any errors."""
    print("error is:",error)

# prints out the final transcript after the twilio call is disconnected
def on_close_channel_1(ws , b ,c ):

    """Upon close, print the complete and final transcript."""
    global LAST_channel_1
    if LAST_channel_1:
        FINALS_channel_1.append(LAST_channel_1)
    transcript = "".join([x['results'][0]['alternatives'][0]['transcript']
                          for x in FINALS_channel_1])
    print(transcript)

# prints out the final transcript after the twilio call is disconnected
def on_close_channel_2(ws , b ,c):

    """Upon close, print the complete and final transcript."""
    global LAST_channel_2
    if LAST_channel_2:
        FINALS_channel_2.append(LAST_channel_2)
    transcript = "".join([x['results'][0]['alternatives'][0]['transcript']
                          for x in FINALS_channel_2])
    print(transcript)

def on_open_channel_1(ws):
    """Triggered as soon a we have an active connection."""
    data = {
        "action": "start",
        # this means we get to send it straight raw sampling
        "content-type": "audio/mulaw;rate=%d" % RATE,
        "interim_results": True,
        "inactivity_timeout": 60, # in order to use this effectively
        # you need other tests to handle what happens if the socket is
        # closed by the server.
        "word_confidence": True,
        "timestamps": True,
        "max_alternatives": 3,
        'smartFormatting': True,
        'splitTranscriptAtPhraseEnd': True,
        'backgroundAudioSuppression': 0.5,
        'speechDetectorSensitivity': 0.4,
    }

    # Send the initial control message which sets expectations for the
    # binary stream that follows:
    try:
        ws.send(json.dumps(data).encode('utf8'))
    except websocket.WebSocketConnectionClosedException as e:
        print("WebSocket connection closed when sending start:", e)
    except Exception as e:
        print("Error sending start message:", e)
    
    # Spin off a dedicated thread where we are going to read and
    # stream out audio.
    threading.Thread(target=read_audio_channel_1, args=(ws,)).start()
    threading.Thread(target=close_transcriber_channel_1, args=(ws,)).start()

def on_open_channel_2(ws):
    """Triggered as soon a we have an active connection."""
    data = {
        "action": "start",
        # this means we get to send it straight raw sampling
        "content-type": "audio/mulaw;rate=%d" % RATE,
        "interim_results": True,
        "inactivity_timeout": 60, # in order to use this effectively
        # you need other tests to handle what happens if the socket is
        # closed by the server.
        "word_confidence": True,
        "timestamps": True,
        "max_alternatives": 3,
        'smartFormatting': True,
        'splitTranscriptAtPhraseEnd': True,
        'backgroundAudioSuppression': 0.5,
        'speechDetectorSensitivity': 0.4,   
       
    }

    # Send the initial control message which sets expectations for the
    # binary stream that follows:
    try:
        ws.send(json.dumps(data).encode('utf8'))
    except websocket.WebSocketConnectionClosedException as e:
        print("WebSocket connection closed when sending start:", e)
    except Exception as e:
        print("Error sending start message:", e)
    
    # Spin off a dedicated thread where we are going to read and
    # stream out audio.
    threading.Thread(target=read_audio_channel_2, args=(ws,)).start()
    threading.Thread(target=close_transcriber_channel_2, args=(ws,)).start()

#send the IBM STT websocket url
def get_url_channel_1():
    load_dotenv()
    url = os.environ['IBM_STT_API_URL']
    url_tail = str(url.split(":")[-1])
    stt_endpoint = "wss:"+url_tail+"/v1/recognize?model="+model
    return(stt_endpoint)

#send the IBM STT websocket url 
def get_url_channel_2():
    load_dotenv()
    url = os.environ['IBM_STT_API_URL']
    url_tail = str(url.split(":")[-1])
    stt_endpoint = "wss:"+url_tail+"/v1/recognize?model="+model
    return(stt_endpoint)

#handles the IBM STT api key
def get_auth_channel_1():
    load_dotenv()
    apikey = os.environ['IBM_STT_API_KEY']
    return ("apikey", apikey)

#handles the IBM STT api key
def get_auth_channel_2():
    load_dotenv()
    apikey = os.environ['IBM_STT_API_KEY']
    return ("apikey", apikey)


def main_transcribe_channel_1():
    # Connect to websocket interfaces
    headers = {}
    userpass = ":".join(get_auth_channel_1())
    headers["Authorization"] = "Basic " + base64.b64encode(
        userpass.encode()).decode()
    url = get_url_channel_1()

    # If you really want to see everything going across the wire,
    # uncomment this. However realize the trace is going to also do
    # things like dump the binary sound packets in text in the
    # console.
    #
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                header=headers,
                                on_message=on_message_channel_1,
                                on_error=on_error_channel_1,
                                on_close=on_close_channel_1)

    print("channel 1 websocket connected")
    ws.on_open = on_open_channel_1
    ws.run_forever()

def main_transcribe_channel_2():
    
    # Connect to websocket interfaces
    headers = {}
    userpass = ":".join(get_auth_channel_2())
    headers["Authorization"] = "Basic " + base64.b64encode(
        userpass.encode()).decode()
    url = get_url_channel_2()
    ws = websocket.WebSocketApp(url,
                                header=headers,
                                on_message=on_message_channel_2,
                                on_error=on_error_channel_2,
                                on_close=on_close_channel_2)
    
    print("channel 2 websocket connected")
    ws.on_open = on_open_channel_2
    ws.run_forever()


