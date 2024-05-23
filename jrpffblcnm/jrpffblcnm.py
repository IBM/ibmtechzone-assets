import os
import smtplib
# import requests
import shutil

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate
from typing import List
import json
from collections import defaultdict

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import EmailStr
#from model import send_to_watsonxai
#from prompt import get_prompt, get_class
import json
from fastapi.encoders import jsonable_encoder


global return_dict
app = FastAPI()

EMAIL_ADDRESS = ""
EMAIL_PASSWORD = ""
SMTP_SERVER = ""
SMTP_PORT = 587

def send_email(sender_email, sender_password, recipient_email, subject, body, attachment_paths):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach multiple files
    for attachment_path in attachment_paths:
        with open(attachment_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=os.path.basename(attachment_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)


@app.post('/upload')
async def upload_file(uploaded_file: UploadFile = File(...)):
    global return_dict
    path = f"{uploaded_file.filename}"
    with open(path, 'w+b') as file:
        shutil.copyfileobj(uploaded_file.file, file)
    return_dict={
        'file': uploaded_file.filename,
        'content': uploaded_file.content_type,
        'path': path,
    }
    return return_dict

@app.post("/process_json/")
async def process_json(file: UploadFile = File(...)):
    try:
        filename=file.filename
        temp_pdf_path=return_dict['path']
        contents = await file.read()
        json_data = json.loads(contents)

        temp_json_path = filename
        
        with open(temp_json_path, "w") as temp_file:
            
                json.dump({ "Factsheet_Response": json.loads(json_data)}, temp_file, indent=4)


        
        
        # temp_pdf_path=pdf_file

        attachment_paths=[temp_json_path, temp_pdf_path]

        body=f"""Dear user,

We have received your request.

Thanks and warm regards,
Soumya"""
          
            


        
        
        send_email(EMAIL_ADDRESS, EMAIL_PASSWORD, recipient_email="", subject=filename,body=body ,attachment_paths=attachment_paths)
     
                
        
            
        os.remove(temp_json_path)
        os.remove(temp_pdf_path )

        # return {"status": "error", "message": "Email sent successfully"}


        return JSONResponse(content={"Factsheet": json.loads(json_data)})
    except Exception as ex:
        return {"status": "error", "message": str(ex)}