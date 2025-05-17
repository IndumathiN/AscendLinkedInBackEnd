from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="./config/.env")

app = Flask(__name__)
CORS(app)

# Load API key and model
api_key = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash', api_key=api_key)

# Tasks
loginToLinkedIn = "Go to LinkedIn website. Do login with the x_username and x_password."
searchJob = "Search for Data Analyst jobs in the United States."
chooseFilter = "Choose Date posted as the last 24 hours."

async def run_linkedin_bot(email: str, password: str, llm):
    sensitive_data = {
        'x_username': email,
        'x_password': password
    }

    config = BrowserConfig(
        headless=False,
        disable_security=True,
    )
    browser = Browser(config=config)
    async with await browser.new_context() as context:
        agentLogin = Agent(
            task=loginToLinkedIn,
            llm=llm,
            sensitive_data=sensitive_data,
            browser=browser,
            browser_context=context,
        )
        agentSearchJob = Agent(
            task=searchJob,
            llm=llm,
            browser=browser,
            browser_context=context,
        )
        agentChooseFilter = Agent(
            task=chooseFilter,
            llm=llm,
            browser=browser,
            browser_context=context,
        )

        await agentLogin.run()
        await agentSearchJob.run()
        await agentChooseFilter.run()

        await browser.close()
        return "Success"

@app.route('/run-bot', methods=['POST'])
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

if __name__ == '__main__':
    app.run(port=5000, debug=True)
