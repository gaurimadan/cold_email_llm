import pdfplumber
import re

def extract_clean_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Remove extra spaces, newlines, and special characters
    clean_text = re.sub(r'\s+', ' ', text).strip()
    
    return clean_text

pdf_text = extract_clean_text("/home/gauri/cold_email_llm/marker/gauri.resume-2.pdf")
print(pdf_text)  
