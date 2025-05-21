from flask import Flask, request, jsonify, render_template_string
import base64
import json
import hmac
import hashlib

app = Flask(__name__)

# Salesforce Connected App Consumer Secret
CONSUMER_SECRET = 'FFE6251BCA3AFB6A3301E39F43597EC67439F8C58EE5F74A0992F40CEA1DC17D'

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
    <title>Salesforce Canvas Payload Viewer</title>
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
        <h2>Salesforce Canvas Payload Viewer</h2>
    </div>
    <div id="secretDisplay">{{ data }}</div>

    <script>
        // Try to read signed_request from query param and POST it
        const params = new URLSearchParams(window.location.search);
        const signedRequest = params.get("signed_request");

        if (signedRequest) {
            console.log("📦 Found signed_request in URL, posting...");
            fetch("/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({ signed_request: signedRequest })
            }).then(() => {
                console.log("✅ POST complete, reloading...");
                window.location.href = "/";
            });
        }
    </script>
</body>
</html>
'''

def decode_signed_request(signed_request, secret):
    try:
        encoded_sig, encoded_payload = signed_request.split('.', 1)

        def b64_decode(data):
            padding = '=' * (4 - len(data) % 4) if len(data) % 4 != 0 else ''
            return base64.urlsafe_b64decode(data + padding)

        sig = b64_decode(encoded_sig)
        payload_json = b64_decode(encoded_payload).decode('utf-8')
        data = json.loads(payload_json)

        expected_sig = hmac.new(
            secret.encode('utf-8'),
            msg=encoded_payload.encode('utf-8'),
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
        print("🔄 POST received")
        print("Form data:", request.form)

        signed_request = request.form.get('signed_request')
        if not signed_request:
            return jsonify({"error": "Missing signed_request"}), 400

        decoded_data, valid = decode_signed_request(signed_request, CONSUMER_SECRET)
        latest_payload = decoded_data
        print("📥 Decoded from Salesforce:\n", json.dumps(decoded_data, indent=2))

        return '', 204

    print("👀 GET received")
    display = json.dumps(latest_payload, indent=2) if latest_payload else "No data submitted yet."
    return render_template_string(HTML_TEMPLATE, data=display)

if __name__ == '__main__':
    app.run(debug=True)
