from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser
from pydantic import SecretStr
import os
from dotenv import load_dotenv
import asyncio 
from browser_use import BrowserConfig

load_dotenv(dotenv_path="./config/.env")

api_key = os.getenv("GEMINI_API_KEY")
x_first_name= os.getenv("FIRST_NAME")
x_last_name= os.getenv("LAST_NAME")
x_email= os.getenv("EMAIL_ID")
x_phone= os.getenv("PHONE_NUMBER")

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', api_key=api_key)

# Basic configuration
config = BrowserConfig(
    headless=True, # headless (default: False) Runs the browser without a visible UI. Note that some websites may detect headless mode.
    disable_security=True,
)

# Define sensitive data
# The model will only see the keys (x_name, x_password) but never the actual values
sensitive_data = {
    'x_username': os.getenv("LINKEDIN_USER"),
    'x_password': os.getenv("LINKEDIN_PASS"),
    'x_first_name': os.getenv("LINKEDIN_FIRST_NAME"),
    'x_last_name': os.getenv("LINKEDIN_LAST_NAME"),
    'x_email': os.getenv("LINKEDIN_EMAIL"),
    'x_phone': os.getenv("LINKEDIN_PHONE")
}



job_link="https://careers.chewy.com/us/en/job/CHINUS6821289EXTERNALENUS/Business-Intelligence-Engineer-III?utm_source=linkedin&utm_medium=phenom-feeds?gh_src=o8ua3y1"
# loginToLinkedIn = "Go to LinkedIn website. " \
# "Do login with the x_username and x_password. " 
# selectSkills = "Read the skills "
# searchJob = "Search for Data Analyst jobs in the United States." 
# chooseFilter = "Choose Date posted as the last 24 hours." 
# openDoc=" Open https://docs.google.com/document/d/1TlkpHOu1lv4oXuvBYEwF7_3fmC2KLqp4EaweOK4-vys/edit?tab=t.0 in browser." 
openjoblink=f"You are a professional job applier, Apply to the job on this link {job_link} using for your client using "\
f"{x_first_name},{x_last_name},{x_email},{x_phone} for first name, last name,"\
f"email and phone number. Your client is a female and she is eligible to work in the US. CLose all the popups." 


async def main():
    # Reuse existing browser
    browser = Browser()
    async with await browser.new_context() as context:
        # agentLogin = Agent(
        #     task=loginToLinkedIn,
        #     llm=llm,
        #     sensitive_data=sensitive_data,
        #     browser=browser,  # Browser instance will be reused
        #     browser_context=context,
        # )
        # agentopendoc=Agent(
        #     task="Open the document in the browser",
        #     llm=llm,
        #     browser=browser,  # Browser instance will be reused
        #     browser_context=context,
        # )
        agentjobapply=Agent(
            task=openjoblink,
            llm=llm,
            browser=browser,  # Browser instance will be reused
            browser_context=context,
        )
      
       
        
        
        # await agentLogin.run()
        # # await agentSelectSkills.run()

        # await agentopendoc.run()
    
        await agentjobapply.run()

        # Manually close the browser
        # await browser.close()
    

asyncio.run(main())