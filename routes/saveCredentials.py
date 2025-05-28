import json
import os
from requests import request
import app
from flask import Blueprint, request, jsonify

@app.route("/saveCredentials", methods=["POST"])
def savelinkedInCredentials():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    credentials = {
    "email": email,
    "password": password
}
    credentials_file = "temp_credentials.json"
    if not os.path.exists(credentials_file):
    # Write the credentials to the file
        with open(credentials_file, "w") as f:
            json.dump(credentials, f, indent=4)
        print("File created and credentials saved.")
    else:
        # Optional: overwrite or update existing file
        with open(credentials_file, "w") as f:
            json.dump(credentials, f, indent=4)
        print("File already existed. Credentials updated.")

    return jsonify({"message": "Success"}), 200