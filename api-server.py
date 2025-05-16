import os
import sys
import asyncio
import traceback

from langchain_google_genai import ChatGoogleGenerativeAI

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Request,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from linkedinLogin import run_linkedin_bot  # Import your function
from dotenv import load_dotenv
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

class Credentials(BaseModel):
    email: str
    password: str

@app.post("/connect")
async def connect(credentials: Credentials):
    print("password *************** ",credentials.password)
    try:
        print("API KEY", api_key)
        result = await run_linkedin_bot(credentials.email, credentials.password,llm)
        return {"message": "Success", "result": result}
    except Exception as e:
        traceback_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        print("Exception during LinkedIn bot run:\n", traceback_str)
        raise HTTPException(status_code=500, detail=f"LinkedIn bot failed:\n{str(e)}")
