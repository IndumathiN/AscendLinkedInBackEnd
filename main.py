from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
import os
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
print("OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))
print("GEMINI_API_KEY =", os.getenv("GEMINI_API_KEY"))

app = FastAPI()
 # gemini example


from langchain_google_genai import ChatGoogleGenerativeAI

# Set up LLM using Google Gemini
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",  # Use the full model path
    google_api_key=os.getenv("GEMINI_API_KEY")  # Your API key from .env
)

# Create the agent
agent = Agent(
    task="What is the difference between LangChain and Gemini?",
    llm=llm
)

# Run the agent (proper async handling)
async def run_agent_ai():
    result = await agent.run()  # Ensure you're calling the async `run` method
    return result

# Execute the async function
result = asyncio.run(run_agent_ai())  # Correctly call run_agent()
print(result)

# Allow frontend to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or set specific frontend domain
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/run-agent")
async def run_agent():
    agent = Agent(
        task="Compare the price of gpt-4o and DeepSeek-V3",
        llm=ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")),
    )
    result = await agent.run()
    return {"result": result}
# asyncio.run(run_agent())

@app.get("/agent")
def ask_openai_question(prompt: str):
    client = OpenAI(
        api_key=""
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content


# Example usage
response = ask_openai_question("Where is India?")
print(response)
