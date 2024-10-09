import fitz
from difflib import SequenceMatcher as SM
from nltk.util import ngrams
import re
import math
from PyPDF2 import PdfReader, PdfWriter

class PDFEditor:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)

    def highlight_fuzzy_text_in_pdf(self, page_number, text_to_highlight, output_path):
        page = self.doc.load_page(page_number - 1)
        hay = page.get_text()
        needle = text_to_highlight
        needle_length = len(needle.split())
        max_sim_val = 0
        max_sim_string = ""
        max_sim_start_idx = 0
        for idx, ngram in enumerate(ngrams(hay.split(), needle_length)):
            hay_ngram = " ".join(ngram)
            similarity = SM(None, hay_ngram, needle).ratio()
            if similarity > max_sim_val:
                max_sim_val = similarity
                max_sim_start_idx = idx
        x0 = math.inf
        y0 = math.inf
        x1 = 0
        y1 = 0
        for word in page.get_text("words")[
            max_sim_start_idx : max_sim_start_idx + needle_length
        ]:
            a, b, c, d, *_ = word
            x0 = min(x0, a)
            y0 = min(y0, b)
            x1 = max(x1, c)
            y1 = max(y1, d)
        page.add_highlight_annot([(x0, y0, x1, y1)])
        self.doc.save(output_path, garbage=4, deflate=True, clean=True)

    def create_single_page_pdf(self, page_number, output_path):
        pdf_writer = PdfWriter()
        page = self.doc.load_page(page_number - 1)
        pdf_writer.add_page(page)
        with open(output_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)



