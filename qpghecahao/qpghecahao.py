#Conert Image Based PDF to text Based PDF
import os
from PyPDF2 import PdfWriter, PdfReader
from pdf2image import convert_from_path
import img2pdf


def pdf2img(pdf_document_path, output_folder):
    print('pdf2img')
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    convert_from_path(pdf_document_path, output_folder=output_folder, fmt="jpeg")
    
    
def split_pdf(pdf_document_path):
    inputpdf = PdfReader(open(pdf_document_path, "rb"))
    for i in range(len(inputpdf.pages)):
        output = PdfWriter()
        output.add_page(inputpdf.pages[i])
        with open(pdf_document_path+"page%s.pdf" % i, "wb") as outputStream:
            output.write(outputStream)



def image2pdf(input_folder, output_path):
    imgs = []
    for fname in os.listdir(input_folder):
        print(fname)
        if not fname.endswith(".jpg"):
            continue
        path = os.path.join(input_folder, fname)
        if os.path.isdir(path):
            continue
        imgs.append(path)
    images = sorted(imgs)
    with open(output_path,"wb") as f:
        print('converting back to pdf')
        f.write(img2pdf.convert(images))


pdf2img("report-1.pdf", "report-1")
image2pdf("report-1", "report-1-converted.pdf")
