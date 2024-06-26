import PyPDF2
from os import listdir

PARENT_FOLDER = r"others"

def file_reader(file_location):
    """
    file_reader will read the provided list of file in specified location and return text as outcome.
    """ 
    # Open the file
    pdfFileObject = open(file_location, 'rb')
    pdfReader = PyPDF2.PdfReader(pdfFileObject)

    # identifying the number of pages
    count = len(pdfReader.pages)
    file_text = ""

    # iterate through the page
    for i in range(count):
        page = pdfReader.pages[i]
        file_text += page.extract_text()

    # return the text results
    return file_text


def PDF_to_text():
    """
    Identify each and every file present in the others folder and convert it into respective text file from PDFs.
    """  
    file_arr = listdir(PARENT_FOLDER)
    content_map = []
    for file in file_arr:
        content_map.append({"file_name":file,"file_content":file_reader(("//").join([PARENT_FOLDER,file]))})
    print(content_map)

PDF_to_text()