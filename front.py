import re
import streamlit as st
from app import get_pdf_text, get_completion, parse_response

st.set_page_config(page_title="Resume Evaluator", page_icon="📄")

st.title("📄 PDF Resume Evaluator")

st.markdown("""
    Upload your resume in PDF format and provide a job description.
    The app will evaluate the resume against the job description and give a score.
    It will also list the skills that match the job description and the skills that are lacking.
""")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

job_description = st.text_area("Enter the Job Description", height=150)

if st.button("Evaluate Resume"):
    if uploaded_file and job_description:
        with st.spinner("Processing PDF..."):
            pdf_text = get_pdf_text(uploaded_file)
        
        if "An error occurred" in pdf_text:
            st.error(pdf_text)
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("PDF Content")
                st.text_area("PDF Content", pdf_text, height=250, disabled=True)
            
            with col2:
                st.subheader("Job Description")
                st.text_area("Job Description Content", job_description, height=250, disabled=True)

            st.subheader("Evaluation Result")
            with st.spinner("Evaluating resume against job description..."):
                response_text = get_completion(pdf_text, job_description)
                
                st.text_area("Raw Response", response_text, height=250)

                evaluation = parse_response(response_text)

                score = evaluation['score'].replace(" ", "")
                
                st.subheader("Score")
                st.markdown(f"""
                    <div style='padding: 20px; border: 2px solid #4CAF50; border-radius: 5px; text-align: center;'>
                        <p style='font-size: 36px; font-weight: bold; color: #4CAF50;'>{score}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Skills Match")
                    skills_match_html = "<ul>"
                    for skill in re.split(r'\*\*?\s*', evaluation["skills_match"].strip()):
                        if skill:
                            skills_match_html += f"<li>{skill.strip()}</li>"
                    skills_match_html += "</ul>"
                    st.markdown(f"""
                        <div style='padding: 10px; border: 2px solid green; border-radius: 5px; color:green;'>
                            {skills_match_html}
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.subheader("Skills Lacking")
                    skills_lacking_html = "<ul>"
                    for skill in re.split(r'\*\*?\s*', evaluation["skills_lacking"].strip()):
                        if skill:
                            skills_lacking_html += f"<li>{skill.strip()}</li>"
                    skills_lacking_html += "</ul>"
                    st.markdown(f"""
                        <div style='padding: 10px; border: 2px solid red; border-radius: 5px;color:red;'>
                            {skills_lacking_html}
                        </div>
                    """, unsafe_allow_html=True)

                st.write("### Areas to Consider")
                areas_to_consider_html = "<ul>"
                for area in re.split(r'\*\*?\s*', evaluation["areas_to_consider"].strip()):
                    if area:
                        areas_to_consider_html += f"<li>{area.strip()}</li>"
                areas_to_consider_html += "</ul>"
                st.markdown(areas_to_consider_html, unsafe_allow_html=True)
    elif not uploaded_file:
        st.error("Please upload a PDF file.")
    elif not job_description:
        st.error("Please enter a job description.")
else:
    st.info("Click the button to evaluate the resume after uploading the PDF and entering the job description.")
