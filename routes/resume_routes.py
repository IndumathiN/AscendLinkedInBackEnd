from io import BytesIO
# from requests import request
from flask import Blueprint, request,jsonify
import asyncio
from services.resumeUpload import extract_resume_data

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
        
        # Convert uploaded file to BytesIO
        pdf_bytes = BytesIO(resume.read())
        pdf_bytes.name = resume.filename  # Set a name attribute like an uploaded file

        # Pass this to your function
        result, status_code = extract_resume_data(pdf_bytes)

        if result["type"] == "resume_data":
            return jsonify(result["content"]), status_code
        else:
            return jsonify({"error": result["content"]}), status_code

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500