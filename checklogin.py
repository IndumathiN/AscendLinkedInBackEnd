import json
import os
import sys
import csv
import nest_asyncio
import asyncio
import logging
from pathlib import Path
from typing import Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext

# --- Setup ---
nest_asyncio.apply()
load_dotenv(dotenv_path="./config/.env", override=True)
api_key = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)
CORS(app)

logger = logging.getLogger(__name__)
controller = Controller()

# -- Model + Config --
model = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', api_key=api_key)
config = BrowserConfig(disable_security=True)

# -- Sensitive Data (login credentials) --
with open("temp_credentials.json", "r") as f:
    creds = json.load(f)
sensitive_data = {
    'x_username': creds.get("email"),
    'x_password': creds.get("password")
}

# -- Prompts --
loginToLinkedIn = "Go to LinkedIn website. Do login with the x_username and x_password."
searchJob = "Search for jobs in the United States for java development skills."
saveSearchedJobs = (
    "For each job found, call the action 'Save jobs to file - with a score how well it fits to my profile' "
    "with the job title, company, link, salary, location, and a fit score between 0.0 and 1.0. "
)
checkLoginSuccessTask = ""  # Optional: Add DOM checking task

# -- Job CSV Schema --
class Job(BaseModel):
    title: str
    link: str
    company: str
    fit_score: float
    location: Optional[str] = None
    salary: Optional[str] = None

@controller.action('Save jobs to file - with a score how well it fits to my profile', param_model=Job)
def save_jobs(job: Job):
    print("📝 save_jobs action triggered.")
    with open('jobs.csv', 'a+', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([job.title, job.company, job.link, job.salary, job.location])
        logger.info(f"✅ Saved job: {job.title} at {job.company}")
    return 'Saved job to file'

# -- Async Job Logic --
async def run_job_search():
    browser = Browser()
    async with await browser.new_context() as context:
        agentLogin = Agent(
            task=loginToLinkedIn,
            llm=model,
            sensitive_data=sensitive_data,
            browser=browser,
            browser_context=context,
        )
        agentSearchJob = Agent(
            task=searchJob,
            llm=model,
            browser=browser,
            browser_context=context,
        )
        agentSaveJobs = Agent(
            task=saveSearchedJobs,
            llm=model,
            controller=controller,
            browser=browser,
            browser_context=context,
        )

        # --- Run LinkedIn Login ---
        login_result = await agentLogin.run()

        if not login_result or "fail" in str(login_result).lower():
            raise ValueError("❌ LinkedIn login failed. Please check credentials or try again.")

        print("✅ LinkedIn login successful.")
        await agentSearchJob.run()
        await agentSaveJobs.run()

# -- Flask Endpoint --
@app.route('/start-jobsearch', methods=['POST'])
def start_job_search():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_job_search())
        return jsonify({"status": "success", "message": "Job search completed."}), 200
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}), 500

# -- Main Runner --
if __name__ == '__main__':
    app.run(port=5000, debug=True)
