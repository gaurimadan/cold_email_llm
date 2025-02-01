import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from utils import clean_text
import pdfplumber
import re

# Function to extract text from uploaded PDF
def extract_clean_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Clean up text (remove excessive whitespace)
    clean_text = re.sub(r'\s+', ' ', text).strip()
    return clean_text

def create_streamlit_app(llm, clean_text):
    st.title("📧 Cold Mail Generator")

    # URL input for job descriptions
    url_input = st.text_input("Enter a URL:", value="")

    # File uploader for PDF upload
    uploaded_pdf = st.file_uploader("Upload your resume (PDF format)", type="pdf")

    submit_button = st.button("Submit")

    if submit_button:
        try:
            # Process URL-based job description
            if url_input:
                loader = WebBaseLoader([url_input])
                data = clean_text(loader.load().pop().page_content)
            else:
                data = None  # No URL entered
            
            # Process uploaded PDF
            if uploaded_pdf is not None:
                pdf_text = extract_clean_text(uploaded_pdf)

            # Use extracted job description and resume to generate emails
            if data:
                jobs = llm.extract_jobs(data)
                for job in jobs:
                    email = llm.write_mail(job,pdf_text)
                    st.code(email, language='markdown')

        except Exception as e:
            st.error(f"An Error Occurred: {e}")

if __name__ == "__main__":
    chain = Chain()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, clean_text)
