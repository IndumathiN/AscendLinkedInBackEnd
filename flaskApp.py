from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

@app.route('/run-bot', methods=['POST'])
def run_prompt():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Call your real LinkedIn prompt function here
    try:
        asyncio.run(open_linkedin(email, password))  # Playwright call
        return jsonify({"status": "success", "message": "Success."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

async def open_linkedin(email, password):
    from playwright.async_api import async_playwright
    print("******inside func*******")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.linkedin.com/login")
        await page.fill('input[name="session_key"]', email)
        await page.fill('input[name="session_password"]', password)
        await page.click('button[type="submit"]')
        await asyncio.sleep(5)  # Wait to see the result
        await browser.close()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
