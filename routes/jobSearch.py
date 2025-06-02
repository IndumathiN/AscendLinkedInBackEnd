# routes/bot_routes.py
import sys
from flask import Blueprint, jsonify, request
import asyncio
from services.job_search import job_search, run_agent_task

jobSearch_bp = Blueprint('jobSearch', __name__)


@jobSearch_bp.route('/jobSearch', methods=['POST'])
def jobSearch():
    print("JOBSEARCH*********************")
    data = request.get_json()
    print(data)
    #sys.exit("Stop*************")
    try:
        result = asyncio.run(job_search(data))
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@jobSearch_bp.route("/jobSearchWorking", methods=["POST"])
def search_jobs():
    query = request.get_json()
    print(query)
    location=query['payload']['position']
    prompt = f"""
    Go to https://www.linkedin.com/jobs.
    Search for {location}.
    Return job titles and companies from the first page.
    """

    result = asyncio.run(run_agent_task(prompt))
    return jsonify({"jobs": result})


