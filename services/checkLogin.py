import os
import logging
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig

# Setup
logger = logging.getLogger(__name__)
nest_asyncio.apply()
load_dotenv(dotenv_path="./config/.env", override=True)

async def linkedinLogin(email: str, password: str):
    # Load model
    api_key = os.getenv("GEMINI_API_KEY")
    model = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', api_key=api_key)

    # Instantiate the browser (do not call start())
    browser = Browser(BrowserConfig())

    # Use persistent session profile
    #Save cookies & storage after login.
    #Reuse the same data for all future tasks with that profile.
    # browser_config = BrowserConfig(profile_name="linkedin_user1")
    # browser = Browser(browser_config)
    # #config = BrowserConfig(profile_name="linkedin_user1")
    # print("Path is ************",browser.profile_path)
    # Sensitive credentials
    sensitive_data = {
        "x_username": email,
        "x_password": password
    }
    print(sensitive_data)
    # Define the login task
    login_task = """
        Go to https://www.linkedin.com/login.
        Log in using the provided x_username and x_password.
        If login is successful, say: 'LOGIN_SUCCESS'.
        If login fails or any error message is shown, say: 'LOGIN_FAILED'.
    """
    
    
    # Create and run the agent
    agent = Agent(task=login_task, llm=model, browser=browser, sensitive_data=sensitive_data)
    page = await agent.run()
    content = str(page)

    # Evaluate result
    if "login_failed" in content.lower():
        print("Failed***********")
        raise Exception("❌ LinkedIn login failed: Invalid credentials or login issue.")
        
    elif "login_success" in content.lower():
        print("Success***********")
        logger.info("✅ LinkedIn login appears successful.")
        return True
    else:
        print("Warning***********")
        logger.warning("⚠️ Unexpected result: " + content)
        return False


