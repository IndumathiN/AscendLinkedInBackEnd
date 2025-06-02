def extract_resume_data(pdf_file):
    """Extract structured data from uploaded resume PDF file and save it to a JSON file."""
    import tempfile
    import os
    import fitz  # PyMuPDF
    import pdfplumber
    from langchain_google_genai import ChatGoogleGenerativeAI
    import json
    import re  # For cleaning JSON strings

    if pdf_file is None:
        return {"type": "error", "content": "No file uploaded"},400

    try:
        # Check if the uploaded file is a PDF
        if not pdf_file.name.endswith(".pdf"):
            return {"type": "error", "content": "Please upload a PDF file"},400

        # Create a temporary file to save the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_file.getvalue())
            temp_path = temp_file.name

        try:
            # Initialize Gemini model
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return {"type": "error", "content": "GEMINI_API_KEY is not set in the environment variables"}
            llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', api_key=api_key)

            # Extract text from the PDF
            text_content = ""
            with pdfplumber.open(temp_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content += text + "\n"

            # Process text content with Gemini if available
            if text_content.strip():
                try:
                    # Prompt for structured data extraction
                    extraction_prompt = f"""
                    You are a resume parsing assistant. Extract the following information from this resume:
                    1. First name and Last name
                    2. Location/address
                    3. Contact information (email, phone)
                    4. Skills (list all technical and soft skills)
                    5. Work experience (company names, job titles, dates, responsibilities)
                    6. Education (degrees, institutions, graduation dates)
                    7. If present, extract demographic information like:
                        - Veteran status
                        - Disability status
                        - Race/ethnicity
                    8. Certifications or relevant licenses
                    Additionally, identify any missing or unclear information that might be needed for job applications.
                    Return the data in a JSON format with the following structure:
                    {{
                        "firstName": "First Name",
                        "lastName": "Last Name",
                        "location": "City, State",
                        "contact": {{
                        "email": "email@example.com",
                        "phone": "123-456-7890"
                        }},
                        "skills": ["Skill 1", "Skill 2", ...],
                        "experience": [
                        {{
                            "company": "Company Name",
                            "title": "Job Title",
                            "dates": "Start Date - End Date",
                            "responsibilities": "Key responsibilities..."
                        }}
                        ],
                        "education": [
                        {{
                            "degree": "Degree Name",
                            "institution": "Institution Name",
                            "graduation_date": "Date"
                        }}
                        ],
                        "certifications": ["Certification 1", "Certification 2", ...],
                        "demographics": {{
                        "veteran_status": "Yes/No/Not specified",
                        "disability_status": "Yes/No/Not specified",
                        "race": "Race/ethnicity/Not specified"
                        }},
                        "missing_information": ["Item 1", "Item 2", ...]
                    }}
                    Here is the resume text content:
                    {text_content}
                    """
                    # Get response from LLM
                    response = llm.invoke(extraction_prompt)
                    if response and hasattr(response, "content"):
                        response_text = response.content
                        # Extract JSON from response
                        json_start = response_text.find('{')
                        json_end = response_text.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_content = response_text[json_start:json_end]
                            try:
                                resume_data = json.loads(json_content)
                                # Save the extracted data to a JSON file
                                with open("extracted_resume_data.json", "w", encoding="utf-8") as output_file:
                                    json.dump(resume_data, output_file, indent=4)
                                return {"type": "resume_data", "content": resume_data}, 200
                            except json.JSONDecodeError:
                                # If direct parsing fails, try to clean the JSON string
                                cleaned_json = re.sub(r'(\w+):\s*([^,}\]]+)', r'"\1": "\2"', json_content)
                                try:
                                    resume_data = json.loads(cleaned_json)
                                    # Save the cleaned data to a JSON file
                                    with open("extracted_resume_data.json", "w", encoding="utf-8") as output_file:
                                        json.dump(resume_data, output_file, indent=4)
                                    return {"type": "resume_data", "content": resume_data}, 200
                                except:
                                    return {"type": "error", "content": "Failed to parse resume data from LLM response"}
                        else:
                            return {"type": "text", "content": response_text}
                    else:
                        return {"type": "error", "content": "No valid response from LLM"}
                except Exception as e:
                    return {"type": "error", "content": f"Error processing PDF text with Gemini: {str(e)}"}

            # If text extraction didn't work or found nothing, try OCR
            return {
                "type": "error",
                "content": "This appears to be an image-based PDF. OCR processing is required but not implemented in this example."
            }
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception as e:
        return {"type": "error", "content": str(e)}