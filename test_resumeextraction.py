import io
from resume_extraction import extract_resume_data

# Path to the local PDF file
pdf_file_path = ".\\Resume.pdf"  # Escape backslashes

# Simulate a file upload by reading the PDF file into a BytesIO object
with open(pdf_file_path, "rb") as f:
    pdf_file = io.BytesIO(f.read())     
    pdf_file.name = "resume.pdf"  # Add a name attribute to mimic an uploaded file

# Call the function
result = extract_resume_data(pdf_file)

# Print the result
print(result)