# main.py
import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_agent(request: Request):
    data = await request.json()
    question = data.get("question")
    print("Got Request**********")
    if not question:
        print("Error**********")
        return {"error": "No question provided."}

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    try:
        response = await llm.ainvoke(question)
        print(question, "response**********", response)
        return {"response": response.content}
    except Exception as e:
        print("Exception**********",str(e))
        return {"error": str(e)}
