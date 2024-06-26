# import
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain.prompts import PromptTemplate
from langchain_text_splitters import SentenceTransformersTokenTextSplitter, RecursiveCharacterTextSplitter
import PyPDF2
import os
from ibm_watsonx_ai.foundation_models import Model
from langchain_core.output_parsers import JsonOutputParser
from langchain.docstore.document import Document
from langchain.chains import LLMChain
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from dotenv import load_dotenv, find_dotenv
import json

_ = load_dotenv(find_dotenv())

PERSIST_FOLDER = "persist"

answer = ResponseSchema(
        name="answer",
        description="The answer for the asked question and provided context",
    )

output_parser = StructuredOutputParser.from_response_schemas([answer])


class QueryEngine:

    def __init__(self, txt_file_location, dir):
        self.file_location = txt_file_location
        self.dir = dir

    def get_credentials(self):
        return {"url": os.getenv("GA_URL"), "apikey": os.getenv("GA_API_KEY")}
    
    def create_persist_folder():
        if not os.path.exists(PERSIST_FOLDER):
            os.makedirs(PERSIST_FOLDER)
    
    def get_response_llm(self, context, query):
        model_id = "ibm/granite-13b-chat-v2"
        project_id = os.getenv("GA_PROJECT_ID")
        space_id = os.getenv("SPACE_ID")
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 1500,
            "repetition_penalty": 1,
        }
        model = Model(
            model_id=model_id,
            params=parameters,
            credentials=self.get_credentials(),
            project_id=project_id,
            space_id=space_id,
        )

        prompt = PromptTemplate(
            template=algo_list_generation, input_variables=["context"]
        )
        prompt = prompt.format(context=context)
        answer = (model.generate_text(prompt))
        chain = prompt | model | output_parser
        result = chain.invoke({"question": "what's the capital of france?"})
        return result
    


    def chunk_data(self):
        # load the document and split it into chunks
        loader = TextLoader(self.file_location)
        documents = loader.load()

        # split it into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_overlap=25, chunk_size = 1000)
        docs = text_splitter.split_documents(documents)

        # Add file names to each chunk
        doc_text = []
        filename = ""
        for doc in docs:
            if "{**" in doc.page_content and "**}" in doc.page_content:
                filename = (doc.page_content).split("{**")[1].split("**}")[0]
            page_content = "[ FROM FILE NAME: "+filename+" ]"  +doc.page_content
            document =  Document(page_content=page_content, metadata={"source": "local"})

            doc_text.append(document)

        # create the embedding function based on sentence transformer
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

        # load it into Chroma
        db = Chroma.from_documents(doc_text, embedding_function, persist_directory=self.dir)


    def find_sim(self, query):
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        db = Chroma(persist_directory=self.dir, embedding_function = embedding_function)
        docs = db.similarity_search(query, k=3)
        return docs
    
    def get_context(self, query):
        docs = self.find_sim(query)
        context = []
        for doc_index in docs:
            context.append(doc_index.page_content)

query_engine = QueryEngine('tmp/merged.txt', PERSIST_FOLDER)
query_engine.chunk_data()
contexts = query_engine.get_context("what is vision of IBM about AI and its field?")

