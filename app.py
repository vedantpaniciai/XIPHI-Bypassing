from flask import Flask, request, jsonify, render_template_string
import base64
import json
import hmac
import hashlib

app = Flask(__name__)

# Your Canvas Consumer Secret (use env var in production)
CONSUMER_SECRET = 'FFE6251BCA3AFB6A3301E39F43597EC67439F8C58EE5F74A0992F40CEA1DC17D'

# In-memory store
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

def decode_signed_request(signed_request, secret):
    try:
        encoded_sig, payload = signed_request.split('.', 1)
        sig = base64.urlsafe_b64decode(encoded_sig + '==')
        data_json = base64.urlsafe_b64decode(payload + '==').decode('utf-8')
        data = json.loads(data_json)

        # Verify the signature
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        if not hmac.compare_digest(sig, expected_sig):
            return {"error": "Signature mismatch"}, False

        return data, True
    except Exception as e:
        return {"error": f"Decoding failed: {str(e)}"}, False

@app.route('/', methods=['GET', 'POST'])
def home():
    global latest_payload

    if request.method == 'POST':
        signed_request = request.form.get('signed_request')
        if not signed_request:
            return jsonify({"error": "Missing signed_request"}), 400

        decoded_data, valid = decode_signed_request(signed_request, CONSUMER_SECRET)
        latest_payload.update(decoded_data)
        print("📥 Received:", decoded_data)

        return jsonify({
            "message": "Signed request processed",
            "valid": valid,
            "data": decoded_data
        }), 200

    # Display latest decoded payload
    display = json.dumps(latest_payload, indent=2) if latest_payload else "No data submitted yet."
    return render_template_string(HTML_TEMPLATE, data=display)

if __name__ == '__main__':
    app.run(debug=True)
