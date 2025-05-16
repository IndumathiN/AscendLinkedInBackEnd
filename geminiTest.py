import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()  # Load GEMINI_API_KEY from .env
print(os.getenv("GEMINI_API_KEY"))
try:
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )

    # Try calling the model
    response = llm.invoke("Say hello!")
    print("✅ API key is valid. Response:", response)

except Exception as e:
    print("❌ Error occurred. API key may be invalid or missing.")
    print("Details:", e)
