import os
import sys
import asyncio
import traceback
import subprocess


from langchain_google_genai import ChatGoogleGenerativeAI

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Request,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from linkedinLogin import run_linkedin_bot  # Import your function
from dotenv import load_dotenv
from browser_use import BrowserConfig

load_dotenv(dotenv_path="./config/.env")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to specific frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)


api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash', api_key=api_key)

config = BrowserConfig(
    headless=True, # headless (default: False) Runs the browser without a visible UI. Note that some websites may detect headless mode.
    disable_security=True,
)

class Credentials(BaseModel):
    email: str
    password: str

@app.post("/connect")
async def connect(credentials: Credentials):
    print("password *************** ",credentials.password)
    try:
        print("API KEY", api_key)
        task = asyncio.create_task(run_linkedin_bot(credentials.email, credentials.password,llm))
        result = await task
        # subprocess.call('./linkedinLogin.py', shell=True)
        return {"message": "Success", "result": "result"}
    except Exception as e:
        traceback_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        print("Exception during LinkedIn bot run:\n", traceback_str)
        raise HTTPException(status_code=500, detail=f"LinkedIn bot failed:\n{str(e)}")
