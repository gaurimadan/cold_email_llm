import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job,pdf_text):
        prompt_email = PromptTemplate.from_template(
       """
        ### JOB DESCRIPTION:
        {job_description}
        
        ### INSTRUCTION:
        You are a student whose name is given in {pdf_text}, an engineering student at MAIT, Delhi. You are seeking job at great firms all over the world
        Your job is to write a cold email to the client regarding the job mentioned above describing your capabilities 
        in fulfilling their needs based on th resume that is {pdf_text}. Focus more on expereince and skills that you will get from {pdf_text}. Word limit is 150 to 200 words.
        Remember you are a student whose name is in {pdf_text}, CSE major at MAIT
        Do not provide a preamble.
        ### EMAIL (NO PREAMBLE):
        
        """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job),"pdf_text":pdf_text})
        return res.content

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))