from flask import Flask, request, jsonify, render_template_string
import os
import json

app = Flask(__name__)

latest_payload = {}

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
    </style>
</head>
<body>
    <div class="top-bar">
        <h2>Salesforce Authenticator</h2>
    </div>
    <div id="secretDisplay">{{ data }}</div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    global latest_payload

    if request.method == 'POST':
        try:
            # Try JSON body
            latest_payload = request.get_json(force=True)
            print("✅ JSON Received from Salesforce:")
            print(json.dumps(latest_payload, indent=2))
        except Exception as e:
            # Fallback to form data
            latest_payload = request.form.to_dict()
            print("⚠️ Form Data Fallback:")
            print(latest_payload)

        print("📩 Headers:")
        print(dict(request.headers))

        return jsonify({"message": "Data received", "data": latest_payload}), 200

    # Format JSON payload for better UI rendering
    formatted_data = (
        json.dumps(latest_payload, indent=2) if latest_payload else "No data submitted yet."
    )
    return render_template_string(HTML_TEMPLATE, data=formatted_data)

if __name__ == '__main__':
    app.run(debug=True)
