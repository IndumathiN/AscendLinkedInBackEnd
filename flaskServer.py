import requests
from flask import Flask, request, jsonify,session
from flask_cors import CORS
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv
from resume_extraction import extract_resume_data
import os
from io import BytesIO

# Load environment variables
load_dotenv(dotenv_path="./config/.env")

app = Flask(__name__)
app.secret_key = "NNLinkedInAutomation"  # Required to use sessions
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
#CORS(app)
CORS(app, supports_credentials=True, origins=["http://localhost:8080"])

#  In-memory temporary storage (cleared when server restarts)
temp_credentials = {}
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

        # page = context.pages[0]  # Assuming job listings are on the same tab
        # await page.wait_for_selector('.jobs-search-results__list-item')  # wait for job list

        # job_elements = await page.query_selector_all('.jobs-search-results__list-item')  # top 10 results
        # jobs = []

        # for job in job_elements[:10]:  # Limit to 10
        #     title_el = await job.query_selector('h3')  # title selector
        #     company_el = await job.query_selector('.job-search-card__subtitle')
        #     time_el = await job.query_selector('time')
        #     link_el = await job.query_selector('a')

        #     job_data = {
        #         "title": await title_el.inner_text() if title_el else "",
        #         "company": await company_el.inner_text() if company_el else "",
        #         "posted": await time_el.get_attribute('datetime') if time_el else "",
        #         "link": await link_el.get_attribute('href') if link_el else "",
        #     }
        #     jobs.append(job_data)

        await browser.close()
        return "success"

@app.route('/run-bot', methods=['POST'])
def handle_run_bot():
    data = request.get_json()
    # email = data.get("email")
    # password = data.get("password")
    print(data)
    email=temp_credentials.get("email")
    password=temp_credentials.get("password")

    #print("Session email ",email ," passworrd *****",password)
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        result = asyncio.run(run_linkedin_bot(email, password, llm))
        return jsonify({"message": "Success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    print("UPLOAD RESUME ************")
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        resume = request.files['resume']
        print("Uploaded file:", resume.filename)

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

@app.route("/saveCredentials", methods=["POST"])
def savelinkedInCredentials():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    # Save credentials in session
    # session["email"] = email
    # session["password"] = password

    temp_credentials["email"] = email
    temp_credentials["password"] = password
    # print("********* email session saved is ",session.get("email"), session.get("password"))
    return jsonify({"message": "Success"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
