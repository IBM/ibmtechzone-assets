import os, shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
from dotenv import load_dotenv
from domain import chat_api
import domain
from model.responses import ChatAnswer, Query, MessageResponse, StreamingResponseModel, ChatAnswerIdResponse, GetAnswerResponse
import logging
import coloredlogs
import uuid

load_dotenv('../.env')
PORT = int(os.getenv("BE_PORT", 8080))

logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv('LOG_LEVEL', 'INFO'),
                    fmt='%(asctime)s %(name)s [%(levelname)s] %(message)s')

app = FastAPI(
    version='1.0.0',
    title='AI CHAT',
    description='AI CHAT',
    servers=[{'url': f'http://0.0.0.0:{PORT}/', 'description': 'Server'}],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/start_answer", response_model=ChatAnswerIdResponse)
async def start_answering(question: Query, background_tasks: BackgroundTasks) -> ChatAnswerIdResponse:
    document = domain.start_async_answer_api()
    background_tasks.add_task(domain.update_answer_api, document, question)
    return ChatAnswerIdResponse(id=document["id"])

@app.post("/get_answer", response_model=GetAnswerResponse)
async def get_answer(request: ChatAnswerIdResponse) -> GetAnswerResponse:
    document = domain.get_answer_api(id=request.id)
    return GetAnswerResponse(id=document['id'], answer=document['answer'], status=document['status'])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
