import json
import nest_asyncio
import asyncio
import csv
import logging
import os
import sys
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from PyPDF2 import PdfReader

from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig

# Setup
logger = logging.getLogger(__name__)
nest_asyncio.apply()
load_dotenv(dotenv_path="./config/.env", override=True)

# Load credentials
with open("temp_credentials.json", "r") as f:
    creds = json.load(f)

sensitive_data = {
    'x_username': creds.get("email"),
    'x_password': creds.get("password")
}

# Model and controller
api_key = os.getenv("GEMINI_API_KEY")
model = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', api_key=api_key)
controller = Controller()

# Prompts
loginToLinkedIn = "Go to LinkedIn website. Do login with the x_username and x_password."
selectSkills = "Read the skills, location from the yml file {userInput}."
#searchJob = "Search for jobs in the United States for java development skills'#{selectedSkills}."
#chooseFilter = "Choose Date posted as the past 24 hours."
saveSearchedJobs = (
    "For each job found, call the action 'Save jobs to file - with a score how well it fits to my profile' "
    "with the job title, company, link, salary, location, and a fit score between 0.0 and 1.0."
)
checkLoginSuccessTask = ""

# Job data model
class Job(BaseModel):
    title: str
    link: str
    company: str
    fit_score: float
    location: Optional[str] = None
    salary: Optional[str] = None

# Save job to CSV
@controller.action('Save jobs to file - with a score how well it fits to my profile', param_model=Job)
def save_jobs(job: Job):
    file_path = 'jobs.csv'
    file_exists = os.path.exists(file_path)
    print("INSIDE CSV func****************")
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)

        # Write headers if file is newly created
        if not file_exists:
            writer.writerow(['Title', 'Company', 'Link', 'Salary', 'Location'])

        writer.writerow([job.title, job.company, job.link, job.salary, job.location])
        logger.info(f"✅ Saved job: {job.title} at {job.company}")
    
    return 'Saved job to file'
    # with open('jobs.csv', 'a+', newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerow([job.title, job.company, job.link, job.salary, job.location])
    #     logger.info(f"✅ Saved job: {job.title} at {job.company}")
    # return 'Saved job to file'

# Main async function
async def job_search(data):
    browser = Browser()
    print(data)
    searchMode=data['payload']['searchMode']
    position=data['payload']['position']
    selected_location=data['payload']['location']
    experience=data['payload']['experience']

    filters = data['payload']['filters']
    true_filter_keys = [k for k, v in filters.items() if v]
    filters_str = ", ".join(true_filter_keys)

    skills = data['payload']['skills']
    selected_skills = ", ".join(str(item) for item in skills)
    print(selected_skills)    
    # print("Enabled Filters:", filters_str)
    # print(position,location,experience)
    if searchMode == 'skills':
        searchJob = f"Search for jobs in the {selected_location } for {selected_skills} skills."
    else:
        searchJob = f"Search for jobs in the {selected_location } for {position} position."
    chooseFilter = "Choose Date posted as the past 24 hours."
    #sys.exit("Stop*************")
    async with await browser.new_context() as context:
        agentLogin = Agent(task=loginToLinkedIn, llm=model, sensitive_data=sensitive_data, browser=browser, browser_context=context)
        #agentCheckLogin = Agent(task=checkLoginSuccessTask, llm=model, browser=browser, browser_context=context)
        agentSelectSkills = Agent(task=selectSkills, llm=model, browser=browser, browser_context=context)
        agentSearchJob = Agent(task=searchJob, llm=model, browser=browser, browser_context=context)
        agentChooseFilter = Agent(task=chooseFilter, llm=model, controller=controller, browser=browser, browser_context=context)
        agentSaveJobsToCSV = Agent(task=saveSearchedJobs, llm=model, controller=controller, browser=browser, browser_context=context)

        await agentLogin.run()
        await agentSearchJob.run()
        await agentSaveJobsToCSV.run()

    return {"status": "success", "message": "Jobs saved to CSV"}
