from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

# In-memory store
latest_payload = {}

# Hosted Salesforce display app
XIPHI_URL = "https://ciaifastapp-dev-ed.develop.lightning.force.com/lightning/n/ci_fast__FastApp"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Salesforce Authenticator</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            font-family: sans-serif;
        }
        .top-bar {
            background-color: #f4f4f4;
            padding: 10px;
            text-align: center;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        }
        #secretDisplay {
            padding: 20px;
            font-family: monospace;
            background-color: #fafafa;
            border-top: 1px solid #ddd;
            white-space: pre-wrap;
        }
        #resultFrame {
            display: none;
            width: 100%;
            height: 100%;
            border: none;
        }
    </style>
</head>
<body>
    <div class="top-bar" id="topBar">
        <h2>Salesforce Authenticator</h2>
    </div>

    <div id="secretDisplay">{{ data }}</div>

    <iframe id="resultFrame"></iframe>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    global latest_payload
    if request.method == 'POST':
        try:
            latest_payload = request.get_json(force=True)
        except:
            latest_payload = request.form.to_dict()
        return jsonify({"message": "Data received", "data": latest_payload}), 200

    return render_template_string(HTML_TEMPLATE, data=latest_payload or "No data submitted yet.")

@app.route('/submitted-data', methods=['GET'])
def get_latest():
    return jsonify(latest_payload or {"message": "No data submitted yet."})

@app.route('/forward-to-xiphi', methods=['POST'])
def forward_to_xiphi():
    try:
        data = request.get_json(force=True)
        # Forward to hosted XIPHI app
        resp = requests.post(XIPHI_URL, json=data)
        return jsonify({
            "message": "Data forwarded to salesforcexiphi",
            "xiphi_status": resp.status_code,
            "xiphi_response": resp.json()
        }), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
