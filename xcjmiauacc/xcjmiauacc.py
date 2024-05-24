import fitz
from difflib import SequenceMatcher as SM
from nltk.util import ngrams
import re, random, math
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
import os

class PDFEditor:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)

    def highlight_fuzzy_text_in_pdf(self, page_number, text_to_highlight, output_path):
        page = self.doc.load_page(page_number - 1)
        hay = page.get_text()
        needle = text_to_highlight
        needle_length = len(needle.split())
        max_sim_val = 0
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
        for word in page.get_text("words")[max_sim_start_idx : max_sim_start_idx + needle_length]:
            a, b, c, d, *_ = word
            x0 = min(x0, a)
            y0 = min(y0, b)
            x1 = max(x1, c)
            y1 = max(y1, d)

        page.add_highlight_annot([(x0, y0, x1, y1)])
        self.doc.save(output_path, garbage=4, deflate=True, clean=True)

    def create_single_page_pdf(self, page_number, input_pdf_path, output_path):
        pdf_writer = PdfWriter()
        with open(input_pdf_path, 'rb') as input_pdf:
            pdf_reader = PdfReader(input_pdf)
            
            if page_number < 1 or page_number > len(pdf_reader.pages):
                raise ValueError("Invalid page number")

            page = pdf_reader.pages[page_number - 1]
            pdf_writer.add_page(page)

            with open(output_path, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)
            print("done")

    def convert_pdf_image(self, path):
        page = convert_from_path(path, 500)[0]
        name = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
        if not os.path.exists('output'):
            os.makedirs('output')
        image_path = f'output/{name}.jpg'
        page.save(image_path, 'JPEG')
        return image_path

# Example usage
pdf_editor = PDFEditor('example.pdf')
pdf_editor.highlight_fuzzy_text_in_pdf(1, 'text to highlight', 'output_highlighted.pdf')
pdf_editor.create_single_page_pdf(1, 'example.pdf', 'output_single_page.pdf')
image_path = pdf_editor.convert_pdf_image('example.pdf')
print(f'Image saved at: {image_path}')
