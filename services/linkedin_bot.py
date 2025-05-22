from browser_use import Agent, Browser, BrowserConfig

loginToLinkedIn = "Go to LinkedIn website. Do login with the x_username and x_password."
searchJob = "Search for Data Analyst jobs in the United States."
chooseFilter = "Choose Date posted as the last 24 hours."

async def run_linkedin_bot(email: str, password: str, llm):
    sensitive_data = {
        'x_username': email,
        'x_password': password
    }

    config = BrowserConfig(headless=False, disable_security=True)
    browser = Browser(config=config)

    async with await browser.new_context() as context:
        agentLogin = Agent(task=loginToLinkedIn, llm=llm, sensitive_data=sensitive_data, browser=browser, browser_context=context)
        agentSearchJob = Agent(task=searchJob, llm=llm, browser=browser, browser_context=context)
        agentChooseFilter = Agent(task=chooseFilter, llm=llm, browser=browser, browser_context=context)

        await agentLogin.run()
        await agentSearchJob.run()
        await agentChooseFilter.run()

        await browser.close()
        return "Success"
