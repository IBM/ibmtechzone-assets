from fastapi import FastAPI, UploadFile, File, Form
from typing import List, Optional,Union
import uvicorn

app = FastAPI()

@app.post("/upload/")
async def upload_files(name: str = Form(...),
                       age: Optional[int] = Form(None),
                       file_data:List[Union[UploadFile, None]] = File(None)):
    """
    Endpoint to upload text data, with both age  and filedata being optional,
    along with optional multiple files.
    """
    # Handle text data if provided
    
    
        
    
    # Handle files if provided
    i=0
    print("yes------------")

    if file_data:
        for file in file_data:
            i=i+1
            print("File Name:", file.filename)
    no_of_files=i
    if age is  None:
        msg=f"no of files  received by {name}  are {no_of_files}"
    else:
        msg=f"no of files  received by {name} with age {age} are {no_of_files}"
        
    return {"message": msg}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

