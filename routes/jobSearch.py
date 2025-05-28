# routes/bot_routes.py
import sys
from flask import Blueprint, jsonify, request
import asyncio
from services.job_search import job_search

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
