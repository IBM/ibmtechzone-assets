import re
from typing import Literal, Optional, Any
import pandas
from langchain.document_loaders import PyPDFLoader

class pdfLoader():
    def __init__(self) -> None:
        pass

    def pdf_to_text(self,
                path: str, 
				start_page: int = 1, 
				end_page: Optional[int | None] = None) -> list[str]:
            """
            Converts PDF to plain text.

            Params:
                path (str): Path to the PDF file.
                start_page (int): Page to start getting text from.
                end_page (int): Last page to get text from.
            """
            loader = PyPDFLoader(path)
            pages = loader.load()

            total_pages = len(pages)

            if end_page is None:
                end_page = len(pages)

            text_list = []
            page_list = []
            for i in range(start_page-1, end_page):
                text = pages[i].page_content
                text = text.replace('\n', ' ')
                text = re.sub(r'\s+', ' ', text)
                text_list.append(text)
                page_list.append(i)

            return (text_list, page_list, pages)
