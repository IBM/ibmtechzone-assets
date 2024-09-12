
from flask import Flask, render_template, jsonify, Response, request
from flask_sock import Sock

from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial, Connect
from twilio.rest import Client
import numpy as np

from dotenv import load_dotenv
import os, ngrok, base64, json
import pprint as p
from IBM_STT import main_transcribe_channel_1,main_transcribe_channel_2, stream, closeTranscriber_channel_1,closeTranscriber_channel_2
import threading
import numpy as np
# from pydub import AudioSegment
# from io import BytesIO
# import asyncio
# from pydub import AudioSegment
# import io
# import audioop

load_dotenv()

# reads the data from env file
account_sid = os.environ['TWILIO_ACCOUNT_SID']  
api_key = os.environ['TWILIO_API_KEY_SID']
api_key_secret = os.environ['TWILIO_API_SECRET']
twiml_app_sid = os.environ['TWIML_APP_SID']
twilio_number = os.environ['TWILIO_NUMBER']

# the websocket which takes the audio file twilio and sends to the IBM_STT.py file for trancription
WEBSOCKET_ROUTE = '/realtime'

# client used to make and receive calls
client = Client(api_key, api_key_secret, account_sid)

# ngrok authentication  
ngrok.set_auth_token(os.getenv('NGROK_AUTHTOKEN'))

#flask application as UI and redirecting
app = Flask(__name__)
sock = Sock(app)

call_info = {}  # Dictionary to store call information

# home page of the UI
@app.route('/')
def home():
    return render_template(
        'home.html',
        title="In browser calls"
    )

# identifies the token and grants the permission
@app.route('/token', methods=['GET'])
def get_token():
    identity = twilio_number
    outgoing_application_sid = twiml_app_sid

    access_token = AccessToken(account_sid, api_key,
                               api_key_secret, identity=identity)
    
    voice_grant = VoiceGrant(
        outgoing_application_sid=outgoing_application_sid,
        incoming_allow=True,
    )
    access_token.add_grant(voice_grant)
    response = jsonify(
        {'token': access_token.to_jwt(), 'identity': identity})

    return response

# twilio's VoiceResponse is initiated and streamed to the websocket to catch the call audio
# ithis method also handles receive and make call 
def handle_call_logic(request_form, host):
    print("host is:",host)
    print("WEBSOCKET_ROUTE is",WEBSOCKET_ROUTE)
    p.pprint(request_form)
    response = VoiceResponse()
    # streams the data to websocket 
    response.start().stream(url=f'wss://{host}{WEBSOCKET_ROUTE}',track='both_tracks')
    
    
    # call from twilio number to personal phone number
    if 'To' in request_form and request_form['To'] != twilio_number:
        print('outbound call')
        dial = Dial(callerId=twilio_number,record='record-from-answer-dual')
        # response.append(connect)
        dial.number(request_form['To'])
        response.append(dial)
    
    # call from personal phone number to twilio number
    else:
        print('incoming call')
        caller = request_form['Caller']
        dial = Dial(callerId=caller)
        # response.append(connect)
        dial.client(twilio_number)
        response.append(dial)
    
    return response

# a websocket to grasp the audio data from call and sends to IBM STT for transcription
@sock.route(WEBSOCKET_ROUTE)
def transcription_websocket(ws):
    
    while True:
        data = json.loads(ws.receive())
        # print("data is:",data)
        match data['event']:
            case "connected":
                print('transcriber connected')
                #channel1 is of customer and channel2 is of agent and IBM STT websocket is initiated for both channels
                threading.Thread(target=main_transcribe_channel_1).start()
                threading.Thread(target=main_transcribe_channel_2).start()
            case "start":
                # indicates the start of twilio for call functionality
                print('twilio started')
            case "media":
                # Assuming message is a base64 encoded string of stereo audio in mulaw format at 8000 Hz
                channel_1 = []   #customer channel
                if data['media']['track'] == 'outbound':
                    
                    payload_b64 = data['media']['payload']
                    channel_1 = base64.b64decode(payload_b64)
                channel_2 = []    #agent channel
                if data['media']['track'] == 'inbound':
                    payload_b64 = data['media']['payload']
                    channel_2 = base64.b64decode(payload_b64)

                # stream is the function in IBM_STT.py which handles the audio and the IBM_STT websocket takes data from stream function.
                stream(channel_1, channel_2)
                
            case "stop":
                #stops the twilio function and also closes the transcription websocket
                print('twilio stopped')
                print('transcriber closed')
                closeTranscriber_channel_1()
                closeTranscriber_channel_2()

# this method handles the call data 
@app.route('/handle_calls', methods=['GET', 'POST'])
def call():
   
    call_data = request.form.to_dict()
    call_sid = request.form.get('CallSid')
    call_info[call_sid] = call_data
    print("call_data is:",call_data)
    print("request.host is:",request.host)
    response = handle_call_logic(call_data, request.host)
 

    return str(response)

if __name__ == "__main__":
    
    # this section handles the code engine public url handling
    try:
        app_url = os.getenv('APP_URL')
        if app_url is None:
            raise ValueError("APP_URL not found")
        
        print("app url is:",app_url)
        # Update the Twilio application with the new URL
        
        twiml_app = client.applications(twiml_app_sid).update(voice_url=f"{app_url}/handle_calls", voice_method="POST")
        app.run(host='localhost', port=8000, debug=False)
    
    # this section handles the ngrok 
    except (ValueError, Exception) as e: 
        print(f"Using Ngrok due to: {e}")
        try:
            # Forward using HTTPS
            listener = ngrok.forward("http://localhost:8000")
            print(f"Ngrok tunnel opened at {listener.url()} for port 8000")
            NGROK_URL = listener.url()
            print("ngrok url is:", NGROK_URL)
            # Update the Twilio application with the new HTTPS Ngrok URL
            twiml_app = client.applications(twiml_app_sid).update(voice_url=f"{NGROK_URL}/handle_calls", voice_method="POST")
            
            # Start the local app
            app.run(host='localhost', port=8000, debug=False)
            # app.run(host='0.0.0.0', port=8000, debug=False)

        finally:
            # Disconnect the Ngrok tunnel
            ngrok.disconnect()


        








