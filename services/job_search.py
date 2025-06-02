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
loginToLinkedIn="Go to https://www.linkedin.com/login.Log in using the provided x_username and x_password."
#loginToLinkedIn = "Go to LinkedIn website. Do login with the x_username and x_password."
#selectSkills = "Read the skills, location from the yml file {userInput}."
#searchJob = "Search for jobs in the United States for java development skills'#{selectedSkills}."
#chooseFilter = "Choose Date posted as the past 24 hours."

# saveSearchedJobs = (
#     "For each job found, call the action 'Save jobs to file - with a score how well it fits to my profile' "
#     "with the job title, company, link, salary, location, and a fit score between 0.0 and 1.0."
# )
saveSearchedJobs = """
From the current job listings on the page, for each job:
- Extract the job title, company name, link to the job post, location, and salary (if shown).
- Estimate a fit score between 0.0 and 1.0 based on relevance to the skills in the job title and description.
- Call the action 'Save jobs to file - with a score how well it fits to my profile'
  with the following parameters: title, company, link, location, salary, and fit_score.
"""
#saveJobs = "Save jobs to file"

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
    searchJob = f"""
        Go to https://www.linkedin.com/jobs.
        In the search bar, type: "{selected_skills} jobs in {selected_location}".
        Press Enter to view results.
        """
    # if searchMode == 'skills':
    #     searchJob = f"Search for jobs in the {selected_location } for {selected_skills} skills."
    # else:
    #     searchJob = f"Search for jobs in the {selected_location } for {position} position."
    chooseFilter = "Choose Date posted as the past 24 hours."
    #sys.exit("Stop*************")
    print(saveSearchedJobs)
    async with await browser.new_context() as context:
        agentLogin = Agent(task=loginToLinkedIn, llm=model, sensitive_data=sensitive_data, browser=browser, browser_context=context)
        #agentCheckLogin = Agent(task=checkLoginSuccessTask, llm=model, browser=browser, browser_context=context)
        #agentSelectSkills = Agent(task=selectSkills, llm=model, browser=browser, browser_context=context)
        agentSearchJob = Agent(task=searchJob, llm=model, browser=browser, browser_context=context)
        agentChooseFilter = Agent(task=chooseFilter, llm=model, controller=controller, browser=browser, browser_context=context)
        agentSaveJobsToCSV = Agent(task=saveJobs, llm=model, controller=controller, browser=browser, browser_context=context)
        job_dict = {
        "title": "Data Scientist",
        "company": "OpenAI",
        "link": "https://example.com/job",
        "fit_score":3.2,
        "salary": "$150K",
        "location": "Remote"
        }
        try:
            await agentLogin.run()
            await agentSearchJob.run()
            #await agentChooseFilter.run()
            await agentSaveJobsToCSV.run()
        except Exception as e:
            print("❌ Error in job pipeline:", e)
    return {"status": "success", "message": "Jobs saved to CSV"}


# Job data model
class Job(BaseModel):
    title: str
    link: str
    company: str
    fit_score: float
    location: Optional[str] = None
    salary: Optional[str] = None

# Save job to CSV
@controller.action('Save jobs to file', param_model=Job)
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

async def run_agent_task(prompt: str):
    api_key = os.getenv("GEMINI_API_KEY")
    model = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', api_key=api_key)
    browser = Browser(BrowserConfig(profile_name="linkedin_user1"))  # SAME profile

    agent = Agent(task=prompt, llm=model, browser=browser)
    page = await agent.run()
    return str(page)

async def save_first_10_jobs(agent):
    print("🔍 Getting job elements from the page...")

    # Step 1: Select all job cards on the LinkedIn results page
    job_cards = await agent.browser.get_elements("div.job-card-container")  # Adjust selector if needed

    # Step 2: Limit to the first 10 jobs
    job_cards = job_cards[:10]

    all_jobs = []

    for card in job_cards:
        # Step 3: Extract job data from each card
        job_data = await agent.browser.extract({
            "title": "h3",               # Replace with correct selector inside card
            "company": "h4",
            "location": ".job-location",
            "link": "a@href",
            "posted": ".job-posted-time"
        }, element=card)

        print("✅ Extracted:", job_data)
        all_jobs.append(job_data)

    # Step 4: Save jobs to CSV locally
    with open("linkedin_jobs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "company", "location", "link", "posted"])
        writer.writeheader()
        writer.writerows(all_jobs)

    return f"✅ Saved {len(all_jobs)} jobs to 'linkedin_jobs.csv'"

async def saveJobs(agent):
    # Step 1: Get the text content of the page
    page_text = await agent.browser.get_text()

    # Step 2: Use the LLM to extract job info from the page
    job_data = await agent.llm.ask(
        f"""Here is the content of the LinkedIn job search page:
        ---
        {page_text}
        ---
        Extract the first job's:
        - title
        - company
        - location
        - link (if available)
        - salary (if available)

        Return as a JSON object like:
        {{
            "title": "...",
            "company": "...",
            "location": "...",
            "link": "...",
            "salary": "..."
        }}"""
    )

    # Step 3: Parse it into dict
    try:
        job_dict = json.loads(job_data)
    except:
        print("❌ Failed to parse job JSON")
        return "Failed to extract job data"

    # Step 4: Call controller action
    return await agent.run("Save jobs to file", input=job_dict)
