import os
import logging
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig

# Setup
logger = logging.getLogger(__name__)
nest_asyncio.apply()
load_dotenv(dotenv_path="./config/.env", override=True)

async def main():
    # Load model
    api_key = os.getenv("GEMINI_API_KEY")
    model = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', api_key=api_key)

    # Just instantiate the Browser — do not call start()
    browser = Browser(BrowserConfig())
    # Sensitive credentials
    sensitive_data = {
        "x_username": "indu.dharshu@gmail.com",
        "x_password": "manisathya"
    }

    # Define the login task
    login_task =  """
                Go to https://www.linkedin.com/login.
                Log in using the provided x_username and x_password.
                If login is successful, say: 'LOGIN_SUCCESS'.
                If login fails or any error message is shown, say: 'LOGIN_FAILED'.
                """

    # Create agent
    agent = Agent(task=login_task, llm=model, browser=browser, sensitive_data=sensitive_data)

    # Run it
    page = await agent.run()
    content = str(page)
    if "login_failed" in content.lower():
        raise Exception("❌ LinkedIn login failed: Invalid credentials or login issue.")
    elif "login_success" in content.lower():
        logger.info("✅ LinkedIn login appears successful.")
    else:
        logger.warning("⚠️ Unexpected result: " + content)

# Run the async main function
asyncio.run(main())
