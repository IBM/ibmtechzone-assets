from pdf2image import convert_from_path
import pytesseract

# Function to extract text from PDF
def parse_pdf_pytesseract(pdf_path, page_number=0) -> str:
    images = convert_from_path(
        pdf_path, first_page=page_number + 1, last_page=page_number + 1
    )
    if not images:
        return "Failed to convert PDF to image"
    page_image = images[0]
    extracted_text = pytesseract.image_to_string(page_image)
    return extracted_text