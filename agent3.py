"""
Goal: Searches for job listings after linkedIn login, saves them to a CSV file.

@dev You need to add GEMINI_API_KEY to your environment variables.
Also you have to install couple of python dependencies like langchain, PyPDF2, etc.
"""
import json
import nest_asyncio
import asyncio
import csv
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
from PyPDF2 import PdfReader

from browser_use import ActionResult, Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
#from browser_use.browser.dom import query_selector_all, get_inner_text

logger = logging.getLogger(__name__)
nest_asyncio.apply()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(dotenv_path="./config/.env", override=True)
api_key = os.getenv("GEMINI_API_KEY")

# userInput = Path.cwd() / './config/job_search_config.yaml'
# if not userInput.exists():
#     raise FileNotFoundError(f'skills set file not found at {userInput}. Please update the file path.')


# Initialize the model
model = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', api_key=api_key)
controller = Controller()

# Basic configuration
config = BrowserConfig(
    #headless=True, # headless (default: False) Runs the browser without a visible UI. Note that some websites may detect headless mode.
    disable_security=True,
)

# Define sensitive data
# The model will only see the keys (x_name, x_password) but never the actual values



with open("temp_credentials.json", "r") as f:
    creds = json.load(f)
sensitive_data = {
    'x_username': creds.get("email"),
    'x_password': creds.get("password")
}
loginToLinkedIn = "Go to LinkedIn website. "  \
"Do login with the x_username and x_password. "
# loginToLinkedIn = """
# Go to LinkedIn website.
# Do login with the x_username and x_password.
# Then check whether login was successful or not.
# If it failed, say 'LOGIN_FAILED' in your final output.
# """
checkLoginSuccessTask = """
Check if I am successfully logged into LinkedIn.

If login failed or any error message appears, return exactly:
LOGIN_FAILED

If login was successful, return exactly:
LOGIN_SUCCESS

Do not return anything else.
"""
selectSkills = "Read the skills, location from the yml file {userInput} "
searchJob = "Search for jobs in the United States for java development skills'#{selectedSkills}." 
chooseFilter = "Choose Date posted as the past 24 hours." 
# saveSearchedJobs = "For each job found, call the action 'Save jobs to file."# - with a score how well it fits to my profile' with the job title, company, link, salary, location, and a fit score between 0.0 and 1.0.\n"
# "Make sure you call the save action for each job to store it in the CSV file."
saveSearchedJobs = (
    "For each job found, call the action 'Save jobs to file - with a score how well it fits to my profile' "
    "with the job title, company, link, salary, location, and a fit score between 0.0 and 1.0. "
    "Make sure you call the save action for each job to store it in the CSV file."
)
print(sensitive_data)
print(searchJob)
#sys.exit("Stop*************")
class Job(BaseModel):
	title: str
	link: str
	company: str
	fit_score: float
	location: Optional[str] = None
	salary: Optional[str] = None

#this function automatically gets triggered with the saveSearchedJobs prompt as the wordings match the controller action
@controller.action('Save jobs to file - with a score how well it fits to my profile', param_model=Job)
def save_jobs(job: Job):
	print("📝 save_jobs action was triggered.")
	with open('jobs.csv', 'a+', newline='') as f:
		writer = csv.writer(f)
		writer.writerow([job.title, job.company, job.link, job.salary, job.location])
		print(f"SAVING: {job.title}")
		print("Saving jobs.csv to:", os.getcwd())
		logger.info(f"✅ Saved job: {job.title} at {job.company}")

	return 'Saved job to file'
# *********check for login fail***********
async def check_login_failed(context: BrowserContext) -> bool:
    # Run JS to look for LinkedIn login error messages
    js = """
    () => {
        const alert = document.querySelector('[role="alert"], .alert, .form__error');
        if (alert) {
            return alert.innerText;
        }
        return null;
    }
    """
    #evaluate_script doesn't work in browser-use
    #Since browser_use is an abstraction layer, you need to let the agent or task itself check for login failure, and extract the error signal from the HTML inside the agent (not from context.evaluate_script()).
    result = await context.evaluate_script(js)
    
    if result:
        print("⚠️ Login error detected:", result)
        if "wrong" in result.lower() or "incorrect" in result.lower() or "problem" in result.lower():
            return True

    # Also fallback to checking if still on login page
    current_url = await context.page.url()
    if "login" in current_url:
        return True

    return False


async def main():
    # Reuse existing browser
    browser = Browser()
    async with await browser.new_context() as context:
        agentLogin = Agent(
            task=loginToLinkedIn,
            llm=model,
            sensitive_data=sensitive_data,
            browser=browser,  # Browser instance will be reused
            browser_context=context,
        )
        agentCheckLogin = Agent(
            task=checkLoginSuccessTask,
            llm=model,
            browser=browser,
            browser_context=context,
)

        agentSelectSkills = Agent(
            task=selectSkills,
            llm=model,
            browser=browser,  # Browser instance will be reused
            browser_context=context,
        )
        agentSearchJob = Agent(
            task=searchJob,
            llm=model,
            browser=browser,  # Browser instance will be reused
            browser_context=context,
        )
        agentChooseFilter = Agent(
            task=chooseFilter,
            llm=model,
            controller=controller,
            browser=browser,  # Browser instance will be reused
            browser_context=context,
        )
        agentSaveJobsToCSV = Agent(
            task=saveSearchedJobs,
            llm=model,
            controller=controller,
            browser=browser,  # Browser instance will be reused
            browser_context=context,
        )
        result_login=await agentLogin.run()
        print("Login attempt completed.")
        await agentSearchJob.run()
        await agentSaveJobsToCSV.run()

        # result_check = await agentCheckLogin.run()

        # try:
        #     print(result_check)
        #     final_action = result_check.all_results[-1]
        #     final_content = getattr(final_action, "extracted_content", "") or ""
        #     print("🔍 Final content:", final_content)

        #     if "LOGIN_FAILED" in final_content.upper():
        #         raise ValueError("❌ LinkedIn login failed. Check credentials.")
        #     elif "LOGIN_SUCCESS" in final_content.upper():
        #         print("✅ Successfully logged in to LinkedIn.")
        #     else:
        #         print("⚠️ Login result unclear:", final_content)

        # except Exception as e:
        #     print("❗ Error interpreting login result:", e)
        #     raise
# Safety check: ensure it's an AgentHistoryList
        

        
        #selectedSkills = await agentSelectSkills.run()
        #print(selectSkills)
        
        # result = await agentCheckLogin.run()
        # if "LOGIN_FAILED" in result:
        #     raise ValueError("❌ LinkedIn login failed. Invalid username or password.")

        # login_failed = await check_login_failed(context)
        # if login_failed:
        #     raise ValueError("❌ LinkedIn login failed: Invalid username or password.")
        #await agentSearchJob.run()
        #await agentChooseFilter.run()
        #await agentSaveJobsToCSV.run()
		

        # Manually close the browser
        #await browser.close() 

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except ValueError as ve:
        print(str(ve))  # 👈 This can be sent as HTTP response to frontend
        sys.exit(1)
    except Exception as e:
        print(f"🔥 Unexpected error: {e}")
        sys.exit(1)

