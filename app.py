from openai import OpenAI
import fitz
from pdf2image import convert_from_bytes
import pytesseract
import re

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="your-api-key-here"
)

def get_completion(file_text, job_description):
    try:
        completion = client.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[{"role": "user", "content": "Evaluate the resume based on the job description and give a score. Additionally, list the skills that match the job description and the skills that are lacking. Only give the score, skills match,Skills lacking, and areas to consider.\n\nResume:\n" + file_text + "\n\nJob Description:\n" + job_description}],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
            stream=True
        )
        
        response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
        
        return response
    except Exception as e:
        return f"An error occurred: {e}"


def get_pdf_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    if not text.strip():
        images = convert_from_bytes(file.read())
        for image in images:
            text += pytesseract.image_to_string(image)
    
    return text


def parse_response(response_text):


    sections = {
        "score": "",
        "skills_match": "",
        "skills_lacking": "",
        "areas_to_consider": ""
    }

    patterns = {
        "score": re.compile(r"Score:\s*([\d\.]+/10)", re.IGNORECASE),
        "skills_match": re.compile(r"Skills Match(?:\s*:|):\s*([\s\S]*?)(?:Skills Lacking:|Areas to Consider:|$)", re.IGNORECASE),
        "skills_lacking": re.compile(r"Skills Lacking(?:\s*:|):\s*([\s\S]*?)(?:Areas to Consider:|$)", re.IGNORECASE),
        "areas_to_consider": re.compile(r"Areas to Consider(?:\s*:|):\s*([\s\S]*)", re.IGNORECASE)
    }

    for key, pattern in patterns.items():
        match = pattern.search(response_text)
        if match:
            sections[key] = match.group(1).strip()
        else:
            sections[key] = "No information available."

    for key in sections:
        if sections[key] != "No information available.":
            sections[key] = "\n".join(line.strip() for line in sections[key].splitlines() if line.strip())

    return sections
