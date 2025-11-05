import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from utils import clean_text
import pdfplumber
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Function to extract text from uploaded PDF
def extract_clean_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    clean_text = re.sub(r'\s+', ' ', text).strip()
    return clean_text


# Function to send email
def send_email(sender_email, sender_password, recipient_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        # Gmail SMTP example — adjust for your provider
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False


def create_streamlit_app(llm, clean_text):
    st.set_page_config(page_title="Cold Email Generator", page_icon="📧")

    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📧 Cold Mail Generator</h1>", unsafe_allow_html=True)

    url_input = st.text_input("Enter a job posting URL:")
    uploaded_pdf = st.file_uploader("Upload your resume (PDF format)", type="pdf")

    # Optional recruiter email
    recruiter_email = st.text_input("Recruiter's Email (optional):")

    # Optional sender credentials (you can hide them with password fields)
    with st.expander("📨 Email Settings (Optional)"):
        sender_email = st.text_input("Your Email Address")
        sender_password = st.text_input("Your Email Password / App Password", type="password")

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
                        email_body = llm.write_mail(job, pdf_text)
                        with st.expander(f"📩 Cold Email for {job['role']}", expanded=True):
                            st.markdown(f"<div style='white-space: pre-wrap; word-wrap: break-word; font-size: 16px; color: #333; padding: 10px; border-radius: 10px; background-color: #f8f9fa;'>{email_body}</div>", unsafe_allow_html=True)

                        # Send email automatically if recruiter email is provided
                        if recruiter_email and sender_email and sender_password:
                            st.info(f"Sending email to {recruiter_email}...")
                            subject = f"Application for {job['role']}"
                            success = send_email(sender_email, sender_password, recruiter_email, subject, email_body)
                            if success:
                                st.success(f"✅ Email successfully sent to {recruiter_email}!")

        except Exception as e:
            st.error(f"❌ An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    create_streamlit_app(chain, clean_text)
