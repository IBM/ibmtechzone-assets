import PyPDF2,os,requests,zipfile
from pdf2image import convert_from_path


# Define the URL to download
wget_url = os.environ["file_path"]
# Create the 'data' directory if it doesn't exist
os.makedirs('data', exist_ok=True)
# Change the current working directory to 'data'
os.chdir('data')
# Get the current working directory
CWD = os.getcwd()
# Download the file from the URL
response = requests.get(wget_url)
file_name = wget_url.split('/')[-1]
file_path = os.path.join(CWD, file_name)
print("file_name ",file_name)
print("file_path ",file_path)
# Write the downloaded content to a file
with open(file_path, 'wb') as file:
    file.write(response.content)
print("file ",file)
# Iterate through all files in the current working directory
for file in os.listdir(CWD):
    if file.endswith('.zip'):
        # Unzip the file
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(CWD)


def is_pdf_image_based(pdf_path):
    # Step 1: Try to extract text using PyPDF2
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text_content = ""
            for page_num in range(len(reader.pages)):
                text_content += reader.pages[page_num].extract_text() or ""

            # If text is found, it's a text-based PDF
            if text_content.strip():
                return False  # PDF is text-based
    except Exception as e:
        print(f"Error while reading PDF with PyPDF2: {e}")

    # Step 2: Convert PDF pages to images to check if it contains image content
    try:
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        # If conversion to images is successful, it suggests the PDF might be image-based
        if images:
            return True  # PDF is image-based
    except Exception as e:
        print(f"Error while converting PDF to image: {e}")

    return False  # Default to text-based if no indication of being image-based

# Path to your PDF file
# pdf_path = "/Users/susmitpanda/Documents/Bancolombia/Archivo/73. 824003151 EEFF CORTE JUN 2023-2024.pdf"
if is_pdf_image_based(file_path):
    print("The PDF is image-based.")
else:
    print("The PDF is text-based.")