from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser
from pydantic import SecretStr
import os
from dotenv import load_dotenv
import asyncio 
from browser_use import BrowserConfig

load_dotenv(dotenv_path="./config/.env")

api_key = os.getenv("GEMINI_API_KEY")
print("API KEY", api_key)
# Initialize the model
# llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', api_key=api_key)
llm = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash', api_key=api_key)
# Basic configuration
config = BrowserConfig(
    headless=True, # headless (default: False) Runs the browser without a visible UI. Note that some websites may detect headless mode.
    disable_security=True,
)

# Define sensitive data
# The model will only see the keys (x_name, x_password) but never the actual values
# sensitive_data = {
#     'x_username': os.getenv("LINKEDIN_USER"),
#     'x_password': os.getenv("LINKEDIN_PASS")
# }

loginToLinkedIn = "Go to LinkedIn website. " \
"Do login with the x_username and x_password. " 
selectSkills = "Read the skills "
searchJob = "Search for Data Analyst jobs in the United States." 
chooseFilter = "Choose Date posted as the last 24 hours." \


async def run_linkedin_bot(email,password):
    # Reuse existing browser
    print("email :",email)
    browser = Browser()
    sensitive_data = {
    'x_username': email,
    'x_password': password
    }
    async with await browser.new_context() as context:
        agentLogin = Agent(
            task=loginToLinkedIn,
            llm=llm,
            sensitive_data=sensitive_data,
            browser=browser,  # Browser instance will be reused
            browser_context=context,
        )
        agentSelectSkills = Agent(
            task=selectSkills,
            llm=llm,
            browser=browser,  # Browser instance will be reused
            browser_context=context,
        )
        agentSearchJob = Agent(
            task=searchJob,
            llm=llm,
            browser=browser,  # Browser instance will be reused
            browser_context=context,
        )
        agentChooseFilter = Agent(
            task=chooseFilter,
            llm=llm,
            browser=browser,  # Browser instance will be reused
            browser_context=context,
        )
        
        await agentLogin.run()
        # await agentSelectSkills.run()
        await agentSearchJob.run()
        await agentChooseFilter.run()

        # Manually close the browser
        await browser.close()

async def run_linkedin_bot1(email, password):
    llm = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash', api_key=os.getenv("GEMINI_API_KEY"))

    sensitive_data = {
        'x_username': email,
        'x_password': password
    }

    browser = Browser()
    async with await browser.new_context() as context:
        agentLogin = Agent(
            task="Go to LinkedIn website. Do login with the x_username and x_password.",
            llm=llm,
            sensitive_data=sensitive_data,
            browser=browser,
            browser_context=context,
        )
        await agentLogin.run()
        await browser.close()

    return "LinkedIn login attempt finished"

# asyncio.run(main())