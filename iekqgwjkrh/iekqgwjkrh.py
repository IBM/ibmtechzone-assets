'''
1.Create a .env file with following variables

project_id=<watsonx-project-id>
api_key=<ibm-cloud-apikey>
cloud_url=<cloud-url-depending-on-your-reservation>


2. Save the fastapi code to be converted as input.py and keep it in the same directory.

3. Execute this script
'''



from ibm_watsonx_ai.foundation_models import Model
import os
from dotenv import load_dotenv
import json
load_dotenv()

project_id = os.getenv("project_id", None)
api_key = os.getenv("api_key", None)
url=os.getenv("cloud_url", None)


model_id = "codellama/codellama-34b-instruct-hf"
parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 1500,
    "stop_sequences": ["\n\n"],
    "repetition_penalty": 1
}
model = Model(
	model_id = model_id,
	params = parameters,
	credentials = {
		"url" : url,
		"apikey" : api_key
	},
	project_id = project_id
	)




file_path = 'input.py'
with open(file_path, 'r') as file:
    file_content = file.read()

prompt_input = '''Create an openapi json file from the following fastapi code

Input: from milvus_watsonx_embeddings import query
from watsonx import watsonx_call
import uvicorn
from fastapi import FastAPI
import os
import pandas as pd
import tabula
import json
from pydantic import BaseModel
import re
import fitz

app = FastAPI()
class Question(BaseModel):
    quest: str

qa_dict = {}


files = os.listdir("./data/")
print(len(files))
for file in files:
    filepath = os.path.join("./data/", file)
    print(filepath)
dfs = tabula.read_pdf(filepath, pages='all')
newlist = [x for x in dfs if len(x)>3]
df=pd.concat(newlist)
df['Unnamed: 0'] = df['Unnamed: 0'].ffill()


def combine_rows(group):
    return pd.Series({
        '流程步驟': '\n'.join(group['流程步驟'].dropna()),
        '說明': '\n'.join(group['說明'].dropna()),
        '應用系統': '\n'.join(group['應用系統'].dropna()),
        '備註': '\n'.join(group['備註'].dropna())
    })

result_df = df.groupby('Unnamed: 0').apply(combine_rows).reset_index()
data_dict = result_df.to_dict(orient='records')

# Convert dictionary to JSON string with ensure_ascii=False
json_data = json.dumps(data_dict, ensure_ascii=False)
print(json_data)
text=json_data
print(text)



abbreviations=f"""1. PCC (Production Control Center)
        2. MIGO (Material Attribute Code)
        3. SAP (System for Automated Data Processing)
        4. QA32/QA11 (Quality Assurance System)
        5. NG (Not Good)
        6. MIR7 (Material Inspection Record 7)
        7. QA33 (Quality Assurance System 33)
        8. WMS (Warehouse Management System)
        9. RFC (Remote Function Call)"""


def get_image(page_num):
    files = os.listdir("./image_pdf/")
    for file in files:
        filepath = os.path.join("./image_pdf/", file)
    print(filepath)
    # Open the PDF file
    pdf_document = fitz.open(filepath)
    print(f"{page_num}:{len(pdf_document)}")

    image_names = []

    if page_num >= len(pdf_document):
        return image_names
    
    page = pdf_document.load_page(page_num)
    images = page.get_images(full=True)
    print(f"got images {len(images)}")

    for img_index, img in enumerate(images):
        print(f"image {img_index}")

        xref = img[0]
        base_image = pdf_document.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        image_name = f"page{page_num+1}_image{img_index}.{image_ext}"
        if len(image_bytes)>28000:
            image_names.append(image_name)
        
    return image_names






@app.post("/clear_session")
async def clear_session():
    global qa_dict
    qa_dict = {}
    return {"output":'cleared'}

@app.post("/get_answer")
async def get_answer(question:Question):
    global qa_dict
    docs=query(question.quest)
    docs_content=''
    for i in range(len(docs)):
        docs_content+=docs[i].page_content+'\n'
    prompt1 = f"""You are given three contexts and a question. Your task is to identify which of these three contexts is better suited for the answer.
    Output should be either context 1 or context 2 or context 3. Do not provide additional notes or explanation. Answer in english

    Context1:
    {docs_content}
    

    Context2:
    {text}
    

    Context3:
    {abbreviations}


    Question:
    {question.quest}

    Answer:"""
    response=watsonx_call('meta-llama/llama-3-70b-instruct',prompt1,10)
    print(response)

    ref=[]
    image_file_names=[]

    if '2' in response:
        prompt2 = f"""You are given context and a question. From the given context, generate answer for the query.\
        Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content.\
        Do not use prior knowledge to generate answer.\
        If you are not able to find answer the given passages , please state that you do not have an answer.\
        Answer in chinese. Do not give any notes or explanation after generating the response. Make sure your answer is accurate according to the context provided.
        
        
        



        Context:
        {text}


        ChatHistory:
        {qa_dict}

        
    
        Question:
        {question.quest}

        Answer:"""
        response2=watsonx_call('mistralai/mixtral-8x7b-instruct-v01',prompt2,1400)
        print(response2)




    elif '3' in response or 'None' in response:
        prompt3 = f"""You are given context and a question. From the given context, generate answer for the query.\
        Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content.\
        Do not use prior knowledge to generate answer.\
        Answer in chinese. Do not give any notes or explanation after generating the response. Make sure your answer is accurate according to the context provided.
        

        Context:
        {abbreviations}


        ChatHistory:
        {qa_dict}


        Question:
        {question.quest}

        Answer:"""
        response2=watsonx_call('mistralai/mixtral-8x7b-instruct-v01',prompt3,140)
        print(response2)
        



    else:
        docs_content=''
        for i in range(len(docs)):
            docs_content+=f"[passage {i}]"+docs[i].page_content+'\n'


        prompt4 = f"""You are given context and a question. From the given context, generate answer in chinese for the query.\
        Do not give any notes or explanation after generating the response. \
        Your output should be two things: 1)The answer for the query and 2) Passage number from which answer is generated as shown below. \
        
        
        Sample output : 
        Answer: answer
        Passage: passage number
        

        Context:
        {docs_content}


        ChatHistory:
        {qa_dict}

        
        
        Question:
        {question.quest}

        Answer:"""
        
        output=watsonx_call("mistralai/mixtral-8x7b-instruct-v01",prompt4,350)
        print(output)
        output.replace("\n","")
        
# Extract sentences before "Passage"
        
        response2 = re.split(r'\bPassage\b', output)[0].strip()
        resp=output.strip()
        numbers_in_passages = re.findall(r'passage (\d+)', resp)
        numbers_list = list(map(int, numbers_in_passages))  
        print(numbers_list)
        for i in range(3):
                # passage=f'[Passage {i+1}]:'
                content=docs[i].page_content
                page=docs[i].metadata['page']
                ref.append([content,page])
        for number in numbers_list:
            image_file_names += get_image(docs[number].metadata['page'])
    qa_dict[question.quest]=response2
    print(qa_dict)
    

    return {"response":response2,'reference':ref,'images':image_file_names}





if __name__ == "__main__":
   uvicorn.run("api:app", host="0.0.0.0", port=8070, reload=True)

Output: {
    "openapi": "3.0.2",
    "info": {
      "title": "Question Answering API",
      "description": "An API for generating answers to questions based on contexts.",
      "version": "1.0.0"
    },
    "servers": [
      {
        "url": "https://abhi-finalhost-20jun.1i2i2s832t0x.us-south.codeengine.appdomain.cloud",
        "description": "Development server"
      }
    ],
    "paths": {
      "/get_answer": {
        "post": {
          "summary": "Get answer to a question",
          "operationId": "getAnswer",
          "requestBody": {
            "required": true,
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Question"
                }
              }
            }
          },
          "responses": {
            "200": {
              "description": "Successful response",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/Response"
                  }
                }
              }
            }
          }
        }
      },
      "/clear_session": {
        "post": {
          "summary": "Clear session data",
          "operationId": "clearSession",
          "responses": {
            "200": {
              "description": "Session cleared",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": "#/components/schemas/ClearSessionResponse"
                  }
                }
              }
            }
          }
        }
      }
    },
    "components": {
      "schemas": {
        "Question": {
          "type": "object",
          "properties": {
            "quest": {
              "type": "string",
              "description": "The question to be answered"
            }
          }
        },
        "Response": {
          "type": "object",
          "properties": {
            "response": {
              "type": "string",
              "description": "The generated answer"
            },
            "reference": {
              "type": "array",
              "items": {
                "type": "array",
                "items": {
                  "type": "string",
                  "description": "Content of the referenced context"
                }
              },
              "description": "An array of arrays containing the content of referenced contexts"
            },
            "images": {
              "type": "array",
              "items": {
                "type": "string",
                "description": "File names of images"
              },
              "description": "A list of image file names"
            }
          }
        },
        "ClearSessionResponse": {
          "type": "object",
          "properties": {
            "output": {
              "type": "string",
              "description": "Confirmation message for clearing the session"
            }
          }
        }
      }
    }
  }
'''
prompt_input+=f"""

Input: {file_content}
    

Output:"""


print("Submitting generation request...")
generated_response = model.generate_text(prompt=prompt_input, guardrails=False)
print(generated_response)

with open('output.json','w') as f:
    f.write(generated_response)