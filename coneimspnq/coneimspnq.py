"""
Sample .env:
API_KEY = 
IBM_CLOUD_URL = https://eu-gb.ml.cloud.ibm.com/
PROJECT_ID = 
embedding_model_name = BAAI/bge-base-en-v1.5
reranker_model_name = cross-encoder/ms-marco-MiniLM-L-6-v2
get_logs = True
MILVUS_HOST = 
MILVUS_PORT = 
MILVUS_USER = 
MILVUS_PASSWORD = 
milvus_collection_name_business_content =
milvus_embedding_model_name = BAAI/bge-base-en-v1.5
"""




from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
import logging
import torch
import os
import numpy as np
from dotenv import load_dotenv
from pymilvus import connections, Collection, utility, FieldSchema, CollectionSchema, DataType
from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods, ModelTypes
from langchain.vectorstores import Milvus
load_dotenv()
import PyPDF2
import re
from PyPDF2 import PdfReader, PdfWriter
import base64
import os
import pandas as pd
import numpy as np
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFDirectoryLoader
from sentence_transformers import CrossEncoder
from pymilvus import (
    connections, utility, FieldSchema, CollectionSchema, DataType, Collection
)
from langchain.embeddings import HuggingFaceEmbeddings
from numpy.linalg import norm
from fpdf import FPDF
from docx import Document
import mammoth
import datetime
import uvicorn
import logging
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import json
import base64
import nest_asyncio
nest_asyncio.apply()
load_dotenv()

class TextEmbedder:
    """
    Implementation of EmbeddingModelLoader Interface 
    """
    def load_embedding_model(self, embedding_model_name: str):
        """
        This function loads a pre-trained text embedding model that can be used for various downstream  tasks.
        It provides a convenient interface for accessing the text embedding functionality.
        
        Args:
            embedding_model_name (str): Name of the text embedding model to be used.
                                        It specifies the pre-trained model that will be loaded or instantiated for text embedding task.
        Returns:
             The loaded text embedding model instance ready for use in downstream tasks.
        
        """
        logging.info(f"Selected text embedding model: {embedding_model_name}")              
            
        if embedding_model_name not in ('all-MiniLM-L6-v2',
                                        'hkunlp/instructor-large',
                                        "BAAI/bge-small-en-v1.5",
                                        'BAAI/bge-base-en-v1.5',
                                        'BAAI/bge-large-en-v1.5'):
            msg = ("Embedding model must be one of 'all-MiniLM-L6-v2'"
                   ",'hkunlp/instructor-large','BAII/bge-small-en-v1.5'"
                   ",'BAII/bge-large-en-v1.5'")
            raise ValueError(msg)
        
        # Check if CUDA (NVIDIA GPU) is available
        if torch.cuda.is_available():
            device = torch.device("cuda")
            print("CUDA is available. Using GPU:", torch.cuda.get_device_name(0))
        elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
            # Check if MPS (Apple Silicon GPU) is available
            device = torch.device("mps")
            print("MPS is available. Using Apple Silicon GPU.")
        else:
            # Fallback to CPU
            device = torch.device("cpu")
            print("CUDA and MPS are not available. Using CPU.")
        
        # Load embedding model
        try:            
            if embedding_model_name in ["all-MiniLM-L6-v2",
                                        'BAAI/bge-small-en-v1.5',
                                        'BAAI/bge-base-en-v1.5',
                                        "BAAI/bge-large-en-v1.5"] :
                embedding_model = SentenceTransformerEmbeddings(model_name=embedding_model_name,model_kwargs = {'device': device})
    
            elif embedding_model_name in ["hkunlp/instructor-large"]:
                embedding_model = HuggingFaceInstructEmbeddings(
                        model_name=embedding_model_name,
                        model_kwargs = {'device': device}
                    )
        except Exception as e:
            logging.exception("Exception while loading text embedding model")
        logging.info(f"Loaded text embedding model: {embedding_model_name}") 
        return embedding_model






class MilvusRAGPDF:
    def __init__(self):
        self.PROJECT_ID = os.getenv('PROJECT_ID')
        self.IBM_CLOUD_URL = os.getenv('IBM_CLOUD_URL')
        self.API_KEY = os.getenv('API_KEY')
        self.MILVUS_HOST = os.getenv('MILVUS_HOST')
        self.MILVUS_PORT = os.getenv('MILVUS_PORT')
        self.MILVUS_USER = os.getenv('MILVUS_USER')
        self.MILVUS_PASSWORD = os.getenv('MILVUS_PASSWORD')
        self.MILVUS_SECURE = True
        self.MILVUS_SERVER_PEM_PATH = './server.pem'
        self.MILVUS_SERVER_NAME = 'localhost'
        self.COLLECTION_NAME = os.getenv('milvus_collection_name_business_content')
        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5", model_kwargs={"device": "cpu"})
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.connect_to_milvus()

    def connect_to_milvus(self):
        connections.connect(
            alias="default", 
            host=self.MILVUS_HOST, 
            port=self.MILVUS_PORT, 
            secure=self.MILVUS_SECURE, 
            #server_pem_path=self.MILVUS_SERVER_PEM_PATH, 
            #server_name=self.MILVUS_SERVER_NAME, 
            user=self.MILVUS_USER, 
            password=self.MILVUS_PASSWORD
        )
        #connections.connect("default", host=os.getenv('MILVUS_HOST'), port="8080", secure=True, server_pem_path="./server.pem", server_name="localhost",user="root",password="4XYg2XK6sMU4UuBEjHq4EhYE8mSFO3Qq")
        #if not utility.has_collection(self.COLLECTION_NAME):
        schema = CollectionSchema(
            fields=[
                FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535, default_value=""),
                FieldSchema(name="docname", dtype=DataType.VARCHAR, max_length=512, default_value=""),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=768)
            ],
            enable_dynamic_fields=False,
            description="Collection with PDF document chunks"
        )
        self.collection = Collection(
                    name=self.COLLECTION_NAME,
                    schema=schema,
                    consistency_level="Strong"
                )
        """    
        self.vector_db = Milvus(
                self.embeddings,
                connection_args={"host":os.getenv('MILVUS_HOST'), "port":"8080", "secure":True, "server_pem_path":"./server.pem", "server_name":"localhost","user":"root","password":"4XYg2XK6sMU4UuBEjHq4EhYE8mSFO3Qq"},
                collection_name=self.COLLECTION_NAME
                )
        self.collection = Collection(self.COLLECTION_NAME)
        """

        # Loading Collection
        #self.collection.load()


    def send_to_watsonxai(self, prompt, model_id="meta-llama/llama-3-70b-instruct"):  
        params = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.MAX_NEW_TOKENS: 500,
            GenParams.TEMPERATURE: 0,
        }
        creds = {
            "url": self.IBM_CLOUD_URL,
            "apikey": self.API_KEY 
        }
        self.model = Model(model_id=model_id, params=params, credentials=creds, project_id=self.PROJECT_ID)
        response = self.model.generate_text(prompt)
        return response

    def create_prompt_new(self, context, question, instruction):
        template = """
        <|system|>
        You are a helpful assistant that answers users questions soley based on the context provided below. 
        Context: {context}
        
        Also make sure to follow the below instructions while generating response
        Instructions:
        1. Based on the context provided answer the question mentioned.
        2. Be concise and clear in your response.
        3. Don't include any irrelevant text like header/footer
        4. If the context provided doesn't answers the questions then respond "Answer not present in business docs" at all costs and nothing else.
        5. Response should strictly be limited to the context provided above.

        Additional Instructions to be followed: {instruction}

        
        Question: {question}
        <|assistant|>
        """
        prompt = template.format(context=context, question=question, instruction=instruction)
        return prompt

    def rag_pipeline(self, query, instruction_query):
        self.query = query
        self.instruction_query=instruction_query
        query_vector = self.embeddings.embed_documents([query])
        search_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
            }
        results = self.collection.search(query_vector, "vector", search_params, limit=16384, output_fields=["docname","pk","text"]) #self.vector_db.max_marginal_relevance_search(self.query, k=50)
        print("#######################")
        l=[]
        for r in results[0]:
            l.append(r.entity.get('docname'))

        retrieved_documents = []
        retrieved_references = []
        for document in results[0]: #results:
            retrieved_documents.append(document.entity.get('text'))
            retrieved_references.append(document.entity.get('docname'))


        pairs = [[query, doc] for doc in retrieved_documents]
        scores = self.cross_encoder.predict(pairs)

        ordered_retrieve_documents = []
        ordered_retrieve_reference = []
        docs = []
        count=0
        for order in np.argsort(scores)[::-1]:
            ordered_retrieve_documents.append(retrieved_documents[order])
            ordered_retrieve_reference.append(retrieved_references[order])
            docs.append(({'page_content':retrieved_documents[order]},{'score':0},{'ref':retrieved_references[order]}))
            count+=1
            if count>3:
                break

        context = "\n\n\n".join(ordered_retrieve_documents[:4])
        reference = ordered_retrieve_reference[0]
        prompt = self.create_prompt_new(context, self.query,self.instruction_query)
        response = self.send_to_watsonxai(prompt)


        pairs = [[response, doc] for doc in retrieved_documents]
        scores = self.cross_encoder.predict(pairs)

        ordered_retrieve_documents = []
        ordered_retrieve_reference = []
        docs = []
        count=0
        for order in np.argsort(scores)[::-1]:
            ordered_retrieve_documents.append(retrieved_documents[order])
            ordered_retrieve_reference.append(retrieved_references[order])
            docs.append(({'page_content':retrieved_documents[order]},{'score':0},{'ref':retrieved_references[order]}))
            count+=1
            if count>3:
                break


            
        

        docnames=[]
        doc_contents=[]
        p_nums=[]
        encoded_content_list=[]
        reference_info = []
        for i in range (0,4):
            docnames.append(ordered_retrieve_reference[i])
            doc_contents.append(ordered_retrieve_documents[i].rstrip())
            num,encoded_content = self.get_page_number(doc_contents[i],docnames[i])
            p_nums.append(num)
            if(num!=0 and (encoded_content not in encoded_content_list)):
                reference_info.append({"docname":docnames[i], "page_numbers":p_nums[i],"page_content":encoded_content})
            encoded_content_list.append(encoded_content)
        if (response=="Answer not present in business docs"):
                reference_info = []
        return response, context, reference_info #list(set(val for dic in reference_info for val in dic.values()))
    
    def get_page_number(self,text_for_matching,docname):
    # Open the pdf file
        print("Starting")
        object = PyPDF2.PdfReader("Uploads/"+docname)

        # Get number of pages
        NumPages = len(object.pages)

        # Enter code here
        String = text_for_matching
        print("#############")
        print(NumPages)
        p_num=-1
        writer=PyPDF2.PdfWriter()

        # Extract text and do the search
        for i in range(0, NumPages):
            PageObj = object.pages[i]
            Text = PageObj.extract_text()
            if (String in Text):
                p_num = i
                writer.add_page(object.pages[p_num])
        with open("pdf_page.pdf", "wb") as out:
            writer.write(out)
        with open("pdf_page.pdf", "rb") as pdf_file:
            pdf_content = pdf_file.read()
            encoded_pdf_content = base64.b64encode(pdf_content)
        return p_num+1,encoded_pdf_content





class MilvusUploadPDF:

    def __init__(self,COLLECTION_NAME=os.getenv('milvus_collection_name_business_content'),embedding_model_name: str = os.getenv('milvus_embedding_model_name')):
        # Constants
        self.MILVUS_HOST = os.getenv('MILVUS_HOST')
        self.MILVUS_PORT = os.getenv('MILVUS_PORT')
        self.MILVUS_USER = os.getenv('MILVUS_USER')
        self.MILVUS_PASSWORD = os.getenv('MILVUS_PASSWORD')
        self.MILVUS_SECURE = True
        self.MILVUS_SERVER_PEM_PATH = './server.pem'
        self.MILVUS_SERVER_NAME = 'localhost'
        self.COLLECTION_NAME = COLLECTION_NAME
        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5", model_kwargs={"device": "cpu"})
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.connect_to_milvus()

    # Function to connect to Milvus
    def connect_to_milvus(self):
        print("=== Start connecting to Milvus ===")
        connections.connect(
            alias="default", 
            host=self.MILVUS_HOST, 
            port=self.MILVUS_PORT, 
            secure=self.MILVUS_SECURE, 
            #server_pem_path=self.MILVUS_SERVER_PEM_PATH, 
            #server_name=self.MILVUS_SERVER_NAME, 
            user=self.MILVUS_USER, 
            password=self.MILVUS_PASSWORD
        )

    def doc_to_docx(self, input_path, output_path):
        with open(input_path, "rb") as doc_file:
            # Read the .doc file
            result = mammoth.convert_to_html(doc_file)
            
            # Write the converted content to a .docx file
            with open(output_path, "wb") as docx_file:
                docx_file.write(result.value.encode('utf-8'))

    def doc_to_pdf(self, doc_path, pdf_path):
        try:
            # Load the .docx file
            doc = Document(doc_path)
            
            # Create a PDF instance
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Set font for the PDF
            pdf.set_font("Arial", size=12)

            # Create a translation table for unsupported characters
            replacements = {
                '\u2013': '-',  # en-dash
                '\u2014': '-',  # em-dash
                '\u2018': "'",  # left single quote
                '\u2019': "'",  # right single quote
                '\u201c': '"',  # left double quote
                '\u201d': '"',  # right double quote
                # Add more replacements as needed
            }

            # Iterate over the paragraphs in the .docx file and add them to the PDF
            for paragraph in doc.paragraphs:
                text = paragraph.text
                for target, replacement in replacements.items():
                    text = text.replace(target, replacement)
                pdf.multi_cell(0, 10, text)
            
            # Output the PDF to the specified path
            pdf.output(pdf_path)
        except:
            pass

    def create_collection(self, collection_name, drop=False):
        connections.connect(
            alias="default", 
            host=self.MILVUS_HOST, 
            port=self.MILVUS_PORT, 
            secure=self.MILVUS_SECURE, 
            #server_pem_path=self.MILVUS_SERVER_PEM_PATH, 
            #server_name=self.MILVUS_SERVER_NAME, 
            user=self.MILVUS_USER, 
            password=self.MILVUS_PASSWORD
        )
        if drop:
            if collection_name in utility.list_collections():
                print("Dropping collection " + collection_name)
                collection = Collection(collection_name)
                collection.drop()
        

        # if utility.has_collection(collection_name):
        schema = CollectionSchema(
            fields=[
                FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535, default_value=""),
                FieldSchema(name="docname", dtype=DataType.VARCHAR, max_length=512, default_value=""),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=768)
            ],
            enable_dynamic_fields=False,
            description="Collection with PDF document chunks"
        )
        return Collection(
            name=collection_name,
            schema=schema,
            consistency_level="Strong"
        )
    
    def get_elements_for_update(self,newrecords, vecs,ids):
        if ids:
            max_id = max(ids)+1
        else:
            max_id = 0
        new_ids = []
        for _,vec in enumerate(newrecords[2]):
            if vecs:
                cosine = list(np.dot(vecs,vec)/(norm(vecs, axis=1)*norm(vec)))
                if max(cosine)>= 0.9999:
                    id = cosine.index(max(cosine))
                    new_ids.append(ids[id])
                else:
                    new_ids.append(max_id)
                    max_id +=1
            else:
                new_ids.append(max_id)
                max_id +=1
    
        final_newrecords = []
        final_newrecords.append(pd.Series(new_ids))
        for entry in newrecords:
            final_newrecords.append(entry)
        
        return final_newrecords

    # Function to insert data into the collection
    def insert_data_to_collection(self, collection, entries):
        search_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
        }
        query_vector = self.embeddings.embed_documents(["what is watsonx"])
        # collection.load()
        result = collection.search(query_vector, "vector", search_params, limit=16384, output_fields=["docname","pk"])
        pk_ids=[]
        for r in result[0]:
            # checking if within existing collection if doc already exists (entries[1][0] is docname currently being pushed)
            if(r.entity.get('docname')==entries[1][0]): 
                pk_ids.append(r.entity.get('pk'))

        expr = "pk in "+str(pk_ids)
        deleted_entries = collection.delete(expr)
        collection.flush()
        print("deleted_entries")
        print(deleted_entries)

        updated_entries=entries
        collection.load()
        collection.insert(updated_entries)
        collection.flush()
        status = str(len(updated_entries[0]))+" chunks pushed"
        return status
    
    # Function to insert data into the collection
    def delete_data(self, filename, drop=False):
            collection = self.create_collection(self.COLLECTION_NAME,drop=drop)
            collection.load()

            search_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
            }

            res = collection.query(
            expr = "pk >= 0", 
            output_fields = ["pk", "docname"]
            )

            pk_ids=[]
            for r in res:
                if(r['docname']==filename):
                    pk_ids.append(r['pk'])


            expr = "pk in "+str(pk_ids)
            deleted_entries = collection.delete(expr)
            print("deleted_entries")
            print(pk_ids)
            print(deleted_entries)
            print(type(deleted_entries))
            status = str(filename)+" related data deleted"
            return status

   # Main function to orchestrate the tasks
    def push_data(self, filename, drop=False):
        file_path = 'Uploads'
        if '.docx' in filename:
            converted_file = filename.replace('.docx', '.pdf')
            self.doc_to_pdf(f"Uploads/{filename}", f"Uploads/{converted_file}")
            os.remove(f'Uploads/{filename}')
            filename = converted_file
        elif '.doc' in filename:
            converted_docx = filename.replace('.doc', '.docx')
            self.doc_to_docx(f"Uploads/{filename}", f"Uploads/{converted_docx}")
            converted_file = filename.replace('.doc', '.pdf')
            self.doc_to_pdf(f"Uploads/{converted_docx}", f"Uploads/{converted_file}")
            os.remove(f'Uploads/{filename}')
            os.remove(f'Uploads/{converted_docx}')
            filename = converted_file
        

        if '.txt' in filename:
            converted_file = filename.replace('.txt', '.pdf')
            text = open(f'Uploads/{filename}', 'r').read()
            pdf = FPDF()
            pdf.add_page()
            pdf.set_xy(0, 0)
            pdf.set_font('arial', 'B', 13.0)
            #pdf.multi_cell(0, 10, text)
            pdf.cell(ln=0, h=5.0, align='L', w=0, txt=text, border=0)
            pdf.output(f'Uploads/{converted_file}', 'F')
            os.remove(f'Uploads/{filename}')
            filename = converted_file

        if '.xlsx' in filename:
            converted_file = filename.replace('.xlsx', '.pdf')
            df = pandas.read_excel(f'Uploads/{filename}')
            text = "\n\n\n".join(df['Column 2'].values)
            pdf = FPDF()
            pdf.add_page()
            pdf.set_xy(0, 0)
            pdf.set_font('arial', 'B', 13.0)
            #pdf.multi_cell(0, 10, text)
            pdf.cell(ln=0, h=5.0, align='L', w=0, txt=text, border=0)
            pdf.output(f'Uploads/{converted_file}', 'F')
            os.remove(f'Uploads/{filename}')
            filename = converted_file

        loader = PyPDFDirectoryLoader(file_path)
        docs = loader.load()
        print(len(docs))

        text_splitter = CharacterTextSplitter(
            separator="\n", 
            chunk_size=1000, 
            chunk_overlap=200
        )

        documentchunks = loader.load_and_split(text_splitter)
        print(len(documentchunks))
        texts = []
        docnames = []

        for chunk in documentchunks:
            texts.append(chunk.page_content)
            docnames.append(filename)

        vectors = self.embeddings.embed_documents(texts)
        entries = [texts, docnames, vectors]
        print(entries)
        # Create collection
        collection = self.create_collection(self.COLLECTION_NAME,drop=drop)

        # Create index
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        collection.create_index(field_name="vector", index_params=index_params)
        collection.load()

        # Insert data to collection
        status = self.insert_data_to_collection(collection, entries)

        return status





milvus_search_params = {
        "metric_type": "IP",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
        }

milvus_business = MilvusRAGPDF()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to a specific origin or origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define dictionaries to store session-related data:
user_log = {}
get_logs_flag = os.getenv('get_logs')


@app.post("/milvus_upload_business_content/")
def milvus_upload(file: UploadFile = File(...),drop: bool = False):
    filename = file.filename
    path = f'Uploads/{filename}'
    if not os.path.exists(path.split('/')[0]):
        os.mkdir(path.split('/')[0])
    try:
        contents = file.file.read()
        with open(path, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    try:           
        milvus_upload = MilvusUploadPDF(os.getenv('milvus_collection_name_business_content'))
        status = milvus_upload.push_data(filename, drop=drop)
        return  {'status':status}
         
    except Exception as e:
        logging.exception("An error occurred: %s", e)
        return {'error': f'{e} ({str(type(e))})'}, 500
    
@app.post("/delete_data/")
def delete_data(request:dict):
    milvus_business_pdf = MilvusUploadPDF(os.getenv('milvus_collection_name_business_content'))  
    status = milvus_business_pdf.delete_data(request["filename"])
    return {
            "status":status
            }

@app.post("/business_content/")
def business_rfi(request:dict):  
    """
    API to handle business related questions .
    Args:
        {
        "question":"What is Watsonx.ai?"
        }
    Returns:
        dict: Containing response from llm using the query provided.
    
    """
    print("request below ########################")
    print(request)
    

    query=request['question']
    instruction_query = request['instruction']
    response, context, reference = milvus_business.rag_pipeline(query=query,instruction_query=instruction_query)
    return {
            "modified_query":query, 'output':response,
            "context":context, "reference":reference
            }


    
@app.post("/milvus_upload/")
def milvus_upload(file: UploadFile = File(...),drop: bool = False): 
    try:
        contents = file.file.read()
        with open('temp.xlsx', 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    try:           
        milvus_upload = MilvusUpload(os.getenv('milvus_collection_name'))
        status = milvus_upload.push_data(drop=drop)
        print(status)
        milvus_upload = MilvusUpload(os.getenv('milvus_collection_name')+"_backup")
        _ = milvus_upload.push_data(drop=False)
        return  {'status':status}
         
    except Exception as e:
        logging.exception("An error occurred: %s", e)
        return {'error': f'{e} ({str(type(e))})'}, 500

  

if __name__ == "__main__":    
    uvicorn.run(app, host="0.0.0.0",port=8501,log_level="info")