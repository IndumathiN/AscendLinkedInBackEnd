from flask import Blueprint, request, jsonify
from services.linkedin_bot import run_linkedin_bot
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./config/.env")

bot_bp = Blueprint('bot', __name__)
llm = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash', api_key=os.getenv("GEMINI_API_KEY"))

@bot_bp.route('/run-bot', methods=['POST'])
def handle_run_bot():
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
