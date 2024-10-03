import re
from PyPDF2 import PdfReader

# Function to extract text from specific pages of a PDF
def get_page_text(filePath, start_page, end_page):
    pages = []
    reader = PdfReader(filePath)
    for i in range(start_page - 1, end_page):
        page = reader.pages[i]
        text = page.extract_text()
        pages.append(text)
    return " ".join(pages)

# Clean the text to remove unnecessary newlines and extra spaces
def clean_text(text):
    # Replace multiple spaces and newlines with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Function to automatically detect sections and split the text based on numbered headings
def split_sections_auto(text):
    # Refined regex to detect sections starting with numbers followed by a period or full-width dot
    section_pattern = re.compile(r'(?<!\d)(?P<section_number>\b\d{1,2})[．\.](?!\d)', re.MULTILINE)

    # Split the text into sections based on the section numbers
    sections = section_pattern.split(text)

    # Create a dictionary to store sections
    result = {}

    # Iterate through the sections, pairing section numbers with their corresponding content
    for i in range(1, len(sections), 2):
        section_number = sections[i].strip()
        section_content = sections[i + 1].strip()

        # Automatically detect and store valid sections (assuming sections are numeric)
        if section_number.isdigit():
            result[section_number] = section_content

    return result

# Example usage:
file_path = "example.pdf"
start_page = 4 #exclude index pages
end_page = 12

# Step 1: Extract text from specific pages in the PDF
extracted_text = get_page_text(file_path, start_page, end_page)

# Step 2: Clean the extracted text
cleaned_text = clean_text(extracted_text)

# Step 3: Automatically split the cleaned text into sections
sections = split_sections_auto(cleaned_text)

# Output the sections
print(sections)
