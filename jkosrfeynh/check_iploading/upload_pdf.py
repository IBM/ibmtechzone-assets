from fastapi import FastAPI, UploadFile, File
import uvicorn

app = FastAPI()


@app.post("/file")
async def upload_file(file: UploadFile = File(...)):
    # Do here your stuff with the file
    return {"filename": file.filename}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)