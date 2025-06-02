from io import BytesIO
import json
import os
import sqlite3
import uuid
# from requests import request
from flask import Blueprint, request,jsonify
import asyncio
from services.resumeUpload import extract_resume_data
from dotenv import load_dotenv

load_dotenv(dotenv_path="./config/.env")

UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER")
DB_PATH=os.getenv("SQLITE_DB_PATH")

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/resumeUpload', methods=['POST'])
def resumeUpload():
    try:
        result = asyncio.run(extract_resume_data())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@resume_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    print("UPLOAD RESUME ************")
    try:
        
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        resume = request.files['resume']
        

        if resume.filename == '':
            return jsonify({'error': 'Invalid file name'}), 400
        
        # Generate a random filename with the original extension
        original_extension = os.path.splitext(resume.filename)[1]  # e.g., '.pdf'
        random_filename = f"{uuid.uuid4().hex}{original_extension}"

        # Save the file
        file_path = os.path.join(UPLOAD_FOLDER, random_filename)
        resume.save(file_path)
        
        # Convert uploaded file to BytesIO
        resume.stream.seek(0)

        pdf_bytes = BytesIO(resume.read())
        pdf_bytes.name = resume.filename  # Set a name attribute like an uploaded file

        # Pass this to your function
        result, status_code = extract_resume_data(pdf_bytes)

        if result["type"] == "resume_data":
            return jsonify({"filename": random_filename,
                             "content":result["content"]}), status_code
        else:
            return jsonify({"error": result["content"]}), status_code

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@resume_bp.route("/saveResume", methods=["POST"])
def save_resume_data():
    try:
        data = request.get_json()
        print("Received resume data:", data)

        # Example schema: name, email, phone, skills (as JSON), etc.
        firstName = data.get("firstName")
        lastName = data.get("lastName")
        contact = data.get("contact", {})  # Get 'contact' object, default to empty dict
        email = contact.get("email")       # Get email from inside contact
        phone = contact.get("phone") 
        location = data.get("location")
        skills = json.dumps(data.get("skills", []))  # Convert list to JSON string
        experience = json.dumps(data.get("experience", []))
        education = json.dumps(data.get("education", []))
        demographics = json.dumps(data.get("demographics", []))
        certification = json.dumps(data.get("certification", []))
        missing_information = json.dumps(data.get("missing_information", []))

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO resumes (firstname, lastname,email, phone, skills,experience,education,demographics,
                       certification,location,missing_information)
            VALUES (?, ?,?, ?, ?,?, ?, ?, ?,?, ?)
        """, (firstName,lastName, email, phone, skills,experience,education,demographics,certification,location,missing_information))

        conn.commit()
        conn.close()

        return jsonify({"message": "Resume data saved successfully"}), 200

    except Exception as e:
        print("Error saving resume data:", e)
        return jsonify({"error": str(e)}), 500
