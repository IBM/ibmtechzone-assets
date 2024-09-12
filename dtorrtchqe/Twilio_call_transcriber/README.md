# Browser Based Calling Using Twilio
Phone calling app between customer (smartphone) and operator (browser) using Twillio 

Applications used:
1. Ngrok: Ngrok is a cross-platform application that creates secure tunnels (paths) to localhost machine. It enables developers to expose a local development server to the Internet with minimal effort.
2. Twilio: Twilio provides Application Programming Interfaces (APIs) that software developers can use to add communications features like voice, video, chat, authentication, and messaging to their applications.
3. IBM Speech to Text: For transcription and speaker identification
4. Python: For codebase


## Setup
### A. Setup Ngrok account:
1. Go to https://ngrok.com/ and signup for free.
2. You can setup Mutli factor authentication if you want.
3. After successful signup, you will be directed to the ngrok dashboard https://dashboard.ngrok.com/
4. Make note of the ngrok authentication token. It will be needed later while setting up the python codebase.
5. Open up Terminal (MacOS) or Command Prompt (Windows). Follow the Installation steps. 

For example: This is a MacOS setup.
   - In Terminal, install ngrok
   - Configure the auth token with the command provided.
   - Execute command `ngrok http http://localhost:<port on which python api is deployed>` in Terminal to start the ngrok engine
   - Now the engine has started. Make note of the Forwarding url. This will be required for creating the TwiMl application.
   It should look like this: `https://691d-2401-4900-65c4-81e5-9534-6ddf-3d52-ec68.ngrok-free.app`
6. Make sure the ngrok engine keeps running to run the entire setup.

Your Ngrok setup is done!

### B. Setup Twilio account:
1. Go to https://www.twilio.com/login and Signup for free.
2. Verify your email address using the verification code received on your registered email.
3. Register your mobile number and verify it.
4. Save the recovery code in case you don't have your phone to verfiy the twilio account.

    #### 1. Register for a free Twilio number:
    1. After successful sign up, you will be directed to the Twilio console https://console.twilio.com/
    2. On the Home Page, Click on the button "Get Phone Number". You will get your free Twilio number
    3. Scroll down on the console home page, you will get following:
        - Account SID
        - Auth Token
        - My Twilio phone number

       Make a note these credentials. These will be required later while setting up the python code.
    4. You can also acess your Twilio number by navigating to Phone Numbers>Manage>Active Numbers in the left hand side menu "Develop".

    Your Twilio account is created!

    #### 2: Create Twilio API Key:
    1. On the Twilio Dashboard, select Account Management from Admin drop down menu.
    2. From Keys & Credentials menu on the left, select API keys & tokens.
    3. Click on Create API key.
    4. Give a name to the key and click on Create.
    5. Save the SID and Secret. These will be required while setting up the python codebase.

    #### 3: Create a TwiML application
    1. Navigate to Phone Numbers>Manage>TwiML apps in the left hand side menu "Develop".
    2. Click on Create new TwiML App on the right upper corner. You will get a form window.
        - Give name to the application.
        - Copy & Paste the Forwarding URL you saved in the ngrok setup in the Request URL for Voice configuration.
        - click Create.
    3. Your TwiML app is ready and should be displaying in the TwiML Apps dashboard.
    4. Click on the TwiML app to open it.
    5. Save the TwiML App SID. This will be required in setting up the python code.
    
    <i>NOTE: Visit this link for more details on creating the TwiML app: https://help.twilio.com/articles/223180928</i>
    
    #### 4: Connect TwiML app with Active Twilio number
    1. Navigate to Phone Numbers>Manage>Active Numbers in the left hand side menu "Develop".
    2. Click the desired number to modify.
    3. Click on Configure Tab.
    4. In the Voice Configuration section, select TwiML App in the 'Configue With' dropdown menu
    5. Next in the 'TwiML App' dropdown, select the TwiML app you created before.

    Your TwiML application is ready and connected with your active twilio number!

### C: Setup IBM Cloud Account:

1. Go to https://cloud.ibm.com/
2. Create an IBM Cloud Account if you do not have one.
3. Go to Manage>Access(IAM). Select API Keys from the left side menu.
4. Click Create to generate an API Key.
5. Give the API Key a name and click Create.
6. Downlaod the the API Key as this will be needed to setup the python code.

### D: Setup IBM Speech to Text service:
1. Go to https://cloud.ibm.com/
2. Click on the Catalog Menu.
3. Select IBM Cloud Catalog in the drop menu and search Speeh to Text in the search box. 
4. Select the Speech to Text service, you will be redirected to the Speech To Service homepage.
5. Select your respective region and create the service.
6. On the IBM Speech To Text homepage, save the credentials API Key & URL. This will be needed while setting up the python code.

Your IBM Speech To Text Service is ready!

### E: Setup the Python code:
1. Clone the repository: https://github.ibm.com/ClientEngineeringJapanProjects/twillio-phone-calling
2. Setup the env file, by providing following 
      - TWIML_APP_SID="your twiml app sid"
      - TWILIO_ACCOUNT_SID="Account SID"
      - TWILIO_API_KEY_SID="your twilio api key sid"
      - TWILIO_API_SECRET="your twilio api key"
      - TWILIO_NUMBER="saved in section B of this document"
      - TWILIO_AUTH_TOKEN="your twilio auth token"
      - TARGET_PHONE_NUMBER="Any Mobile number"
      - NGROK_AUTHTOKEN=" enter your ngrok auth code" saved earlier.
3. Setup the speech.cfg.
    - apikey = IBM Speech to Text service API Key (In section D of this ReadMe)
    - url = IBM Speech to Text service url (In section D of this ReadMe)
4. Open a new terminal. Navigate to the project source directory.
5. Create python virtual environment:
      `python -m venv venv` 
6. Activate the virtual environment:
    - Macos -> `source venv/bin/activate`
7. Install the requirements.txt
    `pip install -r requirements.txt`
8. Run the application
      `python main.py`
      
Application is hosted on your localhost: `http://127.0.0.1:3000/`

Visit the link and start transcribing!

## Troubleshooting
#### Ngrok:

Error: <b>ERR_NGROK_108</b>

Follow these steps:
1. Open a new terminal.
2. Execute command: `lsof -i :<port number on which python code is running>`
You will get the pid of processes running on the port number. 
3. Execute command: `kill <PID of ngrok>`
4. Rerun the python application.
