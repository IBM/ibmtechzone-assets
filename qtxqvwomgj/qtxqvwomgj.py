import boto3
import os
from PyPDF2 import PdfReader, PdfWriter

# Set AWS credentials
aws_access_key_id = ''
aws_secret_access_key = ''
aws_region = ''



textract_client = boto3.client('textract', 
                               aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key,
                               region_name=aws_region)

def extract_text_from_pdf(pdf_path):
    # Read PDF file
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        extracted_text = ''  # To store text from all pages
        
        # Iterate through each page of the PDF
        for page_num, page in enumerate(pdf_reader.pages):
            # Create a temporary file for the single page PDF
            temp_output_path = f"temp_page_{page_num + 1}.pdf"
            pdf_writer = PdfWriter()
            pdf_writer.add_page(page)
            
            with open(temp_output_path, 'wb') as temp_output_file:
                pdf_writer.write(temp_output_file)
            
            # Call Textract API to detect text for the single page PDF
            with open(temp_output_path, 'rb') as single_page_file:
                response = textract_client.detect_document_text(Document={'Bytes': single_page_file.read()})
                
                # Extract text from response
                for item in response['Blocks']:
                    if item['BlockType'] == 'LINE':
                        extracted_text += item['Text'] + '\n'
                
            # Remove the temporary single page PDF file
            os.remove(temp_output_path)
        
        return extracted_text.strip()




def main():
    input_folder = 'input'  # Folder containing multi-page PDF files
    output_folder = 'output'  # Folder to save extracted text files

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through PDF files in input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            input_filepath = os.path.join(input_folder, filename)
            extracted_text = extract_text_from_pdf(input_filepath)
            output_filename = f"{os.path.splitext(filename)[0]}.txt"
            output_filepath = os.path.join(output_folder, output_filename)
            with open(output_filepath, 'w', encoding='utf-8') as output_file:
                output_file.write(extracted_text)
            print(f"Text extracted from '{filename}'.")

if __name__ == "__main__":
    main()


