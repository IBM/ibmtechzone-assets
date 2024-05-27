import os
import glob
from pdf2docx import parse
from docx import Document


pdf_path = "/Users/satpremrath/Documents/"
pdf_file = "The_Secret_of_the_Enchanted_Forest.pdf"
docx_file = f"{pdf_file[:-4]}.docx"


from pdf2docx import Converter

def convert_pdf_to_docx(pdf_path, docx_path):
    # Create a Converter object
    cv = Converter(pdf_path)
    
    # Convert the PDF to DOCX
    cv.convert(docx_path, start=0, end=None)
    
    # Close the Converter object
    cv.close()


def extract_text_without_strikethrough(docx_path):
    document = Document(docx_path)
    extracted_text = []
    for para in document.paragraphs:
        new_text = ''
        for run in para.runs:
            if not run.font.strike:  # Check if the run is not strikethrough
                new_text += run.text
        if new_text:
            extracted_text.append(new_text)
    return '\n'.join(extracted_text)

# print(lst)

if __name__ == "__main__":
    pdf_path = f"{pdf_path}/{pdf_file}"
    docx_path = f"./{docx_file}"
    convert_pdf_to_docx(pdf_path, docx_path)

    print(extract_text_without_strikethrough(docx_path))
