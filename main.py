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
    st.set_page_config(page_title="Cold Email Generator", page_icon="📧")

    # Page title with styling
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📧 Cold Mail Generator</h1>", unsafe_allow_html=True)
    
    url_input = st.text_input("Enter a job posting URL:")

  
    uploaded_pdf = st.file_uploader("Upload your resume (PDF format)", type="pdf")


    st.markdown("<div style='text-align: center;'><br>", unsafe_allow_html=True)
    submit_button = st.button("🔍 Generate Cold Email")
    st.markdown("</div>", unsafe_allow_html=True)

    if submit_button:
        try:
            with st.spinner("Processing..."):
                pdf_text = ""
                
              
                if url_input:
                    loader = WebBaseLoader([url_input])
                    data = clean_text(loader.load().pop().page_content)
                else:
                    data = None 

            
                if uploaded_pdf is not None:
                    pdf_text = extract_clean_text(uploaded_pdf)

             
                if data:
                    jobs = llm.extract_jobs(data)
                    
                 
                    for job in jobs:
                        email = llm.write_mail(job, pdf_text)
                        with st.expander(f"📩 Cold Email for {job['role']}", expanded=True):
                            st.markdown(f"<div style='white-space: pre-wrap; word-wrap: break-word; font-size: 16px; color: #333; padding: 10px; border-radius: 10px; background-color: #f8f9fa;'>{email}</div>", unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"❌ An Error Occurred: {e}")

if __name__ == "__main__":
    chain = Chain()
    create_streamlit_app(chain, clean_text)
