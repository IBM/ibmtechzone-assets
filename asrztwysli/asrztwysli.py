from fastapi import FastAPI, UploadFile, File, Form
import uvicorn

app = FastAPI()

#here name is one parameter and file_data is another parameter

@app.post("/upload/")
def upload_file(name: str = Form(...), file_data: UploadFile = File(...)):
    """
    Endpoint to upload both text data and a file.
    """
    # Handle text data
    print("Text Data:", name)
    
    # Handle file data
    
    print("File Name:", file_data.filename)
    
    return {"message": f"{file_data.filename} uploaded by {name}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
