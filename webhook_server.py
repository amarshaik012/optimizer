import os
import requests
import zipfile
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Repo details
GITHUB_REPO = "amarshaik012/optimizer"
DOWNLOAD_DIR = "artifacts"

# --- FLASK APP ---
app = Flask(__name__)

# Ensure artifacts folder exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- WEBHOOK ---
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "✅ Webhook endpoint is live. Send a POST request to trigger.", 200

    try:
        event = request.headers.get("X-GitHub-Event")
        payload = request.get_json()
        print(f"🔔 Event received: {event}")

        if event == "workflow_run" and payload["action"] == "completed":
            print("✅ Workflow completed! Fetching artifacts...")
            workflow_run_id = payload["workflow_run"]["id"]

            url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{workflow_run_id}/artifacts"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            resp = requests.get(url, headers=headers)

            if resp.status_code != 200:
                print(f"❌ Error fetching artifacts: {resp.text}")
                return jsonify({"status": "error"}), 500

            artifacts = resp.json().get("artifacts", [])
            downloaded = []

            for artifact in artifacts:
                artifact_name = artifact["name"]
                artifact_id = artifact["id"]

                download_url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/artifacts/{artifact_id}/zip"
                r = requests.get(download_url, headers=headers)

                zip_path = os.path.join(DOWNLOAD_DIR, f"{artifact_name}.zip")
                with open(zip_path, "wb") as f:
                    f.write(r.content)

                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    extract_path = os.path.join(DOWNLOAD_DIR, artifact_name)
                    os.makedirs(extract_path, exist_ok=True)
                    zip_ref.extractall(extract_path)

                downloaded.append(artifact_name)

            return jsonify({"status": "success", "artifacts": downloaded}), 200

        return jsonify({"status": "ignored"}), 200

    except Exception as e:
        print("⚠️ Error handling webhook:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/", methods=["GET"])
def home():
    return "✅ Webhook server is running on /webhook", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6060)
