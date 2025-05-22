from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os
import asyncio
# Load .env file
load_dotenv(dotenv_path="./config/.env")

# Load API Key
api_key = os.getenv("GEMINI_API_KEY")
# print("API KEY ",api_key)
# assert api_key is not None, "❌ GEMINI_API_KEY not found in .env"
llm = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash', api_key=api_key)

# Tasks
loginToLinkedIn = "Go to LinkedIn website. Do login with the x_username and x_password."
searchJob = "Search for Data Analyst jobs in the United States."
chooseFilter = "Choose Date posted as the last 24 hours."

async def run_linkedin_bot(email: str, password: str,llm):
    print("********running chatbot*********")
    # Define sensitive data
    sensitive_data = {
        'x_username': email,
        'x_password': password
    }

    # Initialize browser
    # p = await async_playwright().start()
    # browser = await p.chromium.launch()
    config = BrowserConfig(
        headless=True, # headless (default: False) Runs the browser without a visible UI. Note that some websites may detect headless mode.
        disable_security=True,
    )
    browser = Browser()
    print("********browser created dsf*********")
   # browser = Browser(config=config)
    async with await browser.new_context() as context:
        # Define agents
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

        print("********Before Running agents*********")
        # Run agents
        await agentLogin.run()
        print("********after agentLogin *********")
        await agentSearchJob.run()
        await agentChooseFilter.run()

        await browser.close()
        return "✅ LinkedIn bot completed"
# asyncio.run(run_linkedin_bot(os.getenv("LINKEDIN_EMAIL"), os.getenv("LINKEDIN_PASS"),llm))
