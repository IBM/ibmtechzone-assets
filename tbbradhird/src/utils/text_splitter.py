from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter
from langchain.docstore.document import Document

class langChainRCTSplitter:
    def __init__(self, pages_text, page_num) -> None:
        self.docs = []

        for (page_text, num) in zip(pages_text, page_num):
            langDoc =  Document(page_content=str(page_text), metadata={"page_number": str(num)})
            self.docs.append(langDoc)

    def split_lang_docs(self):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(self.docs)
        return splits
    

class langChainTTSplitter:
    #TODO: pip install tiktoken
    def __init__(self, pages_text, page_num) -> None:
        self.docs = []

        for page_text in zip(pages_text, page_num):
            langDoc =  Document(page_content=str(page_text), metadata={"page_number": str(page_num)})
            self.docs.append(langDoc)

    def split_lang_docs(self):
        text_splitter = TokenTextSplitter(chunk_size=100, chunk_overlap=20)
        splits = text_splitter.split_text(self.docs)
        return splits