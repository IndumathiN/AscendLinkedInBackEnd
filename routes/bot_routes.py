import json
import sys
from flask import Blueprint, request, jsonify
from routes.jobSearch import jobSearch
from services.checkLogin import linkedinLogin
from services.linkedin_bot import run_linkedin_bot
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./config/.env")

bot_bp = Blueprint('bot', __name__)
llm = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash', api_key=os.getenv("GEMINI_API_KEY"))

#@bot_bp.route('/run-bot', methods=['POST'])
def handle_run_bot_old():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        result = asyncio.run(run_linkedin_bot(email, password, llm))
        return jsonify({"message": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bot_bp.route('/run-bot', methods=['POST'])
def handle_run_bot():
    data = request.get_json()
    print(data)
    with open("temp_credentials.json", "r") as f:
        creds = json.load(f)
    email=creds.get("email")
    password=creds.get("password")

    print("Session email ",email ," passworrd *****",password)
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        #result = asyncio.run(run_linkedin_bot(email, password, llm))
        result = asyncio.run(jobSearch())
        return jsonify({"message": "Success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Working with linkedIn login credential check by logging in the website & checking & storing in temp_credentials.json
@bot_bp.route("/saveCredentials", methods=["POST"])
def savelinkedInCredentials():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    credentials = {
    "email": email,
    "password": password
}
    try:
        checkLoginStatus = asyncio.run(linkedinLogin(email, password))
        print("Login Result:", checkLoginStatus)

        if not checkLoginStatus:
            return jsonify({"error": "LinkedIn login failed. Please check credentials."}), 401
        
        credentials_file = "temp_credentials.json"
        if not os.path.exists(credentials_file):
        # Write the credentials to the file
            with open(credentials_file, "w") as f:
                json.dump(credentials, f, indent=4)
            print("✅ File created and credentials saved.")
        else:
            # Optional: overwrite or update existing file
            with open(credentials_file, "w") as f:
                json.dump(credentials, f, indent=4)
            print("✅ File already existed. Credentials updated.")
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        print("❌ Error during LinkedIn login:", str(e))
        return jsonify({"error": f"Exception during login: {str(e)}"}), 500
    #return jsonify({"message": "Success"}), 200