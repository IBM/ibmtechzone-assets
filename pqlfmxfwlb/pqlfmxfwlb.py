from tqdm import tqdm
from pdf2image import convert_from_path
import pytesseract
from uuid import uuid4
import os
import pandas as pd

def get_page_text(filePath):
    doc = convert_from_path(filePath)
    pages = []
    i = 0
    for pageImage in tqdm(doc):
        i += 1
        imagePath = f"{image_dir}{uuid4()}.jpeg"
        pageImage.save(imagePath)
        text = pytesseract.image_to_string(pageImage, lang='jpn')
        pages.append({"Page Number": i, "Text": text, "ImagePath": imagePath})
    return pages


filepath = "toyota.pdf"
image_dir = "image/"
pages = get_page_text(filepath)