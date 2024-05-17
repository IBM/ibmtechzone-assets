import os

import sys
import ocrmypdf

input_file_path = sys.argv[1]
out_file_path = sys.argv[2]


def scannedPdfConverter(file_path, save_path):
    ocrmypdf.ocr(file_path, save_path, skip_text=True)
    print("File converted successfully!")


if out_file_path.split(".")[-1] != "pdf":
    out_file_path = os.path.join(out_file_path, "converted_pdf.pdf")


scannedPdfConverter(input_file_path, out_file_path)
