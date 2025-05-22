from flask import Flask, request, render_template_string
import base64
import json
import hmac
import hashlib

app = Flask(__name__)

# Replace with your Connected App Consumer Secret
CONSUMER_SECRET = 'FFE6251BCA3AFB6A3301E39F43597EC67439F8C58EE5F74A0992F40CEA1DC17D'

latest_payload = {}

def b64_decode(data):
    data += '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data)

def decode_signed_request(signed_request, secret):
    try:
        encoded_sig, encoded_payload = signed_request.split('.', 1)
        sig = b64_decode(encoded_sig)
        payload_json = b64_decode(encoded_payload).decode('utf-8')
        data = json.loads(payload_json)

        expected_sig = hmac.new(
            secret.encode('utf-8'),
            msg=encoded_payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        if not hmac.compare_digest(sig, expected_sig):
            return {"error": "Signature mismatch"}

        return data
    except Exception as e:
        return {"error": f"Decoding failed: {str(e)}"}

@app.route('/', methods=['GET'])
def home():
    display_data = json.dumps(latest_payload, indent=2) if latest_payload else "No data submitted yet."
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Salesforce Canvas Payload Viewer</title>
        <script src="https://login.salesforce.com/canvas/sdk/js/63.0/canvas-all.js"></script>
        <script defer src="/static/post-signed-request.js"></script>
        <style>
            body {
                font-family: sans-serif;
                padding: 20px;
            }
            pre {
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <h2>Salesforce Canvas Payload</h2>
        <pre>{{ data }}</pre>
    </body>
    </html>
    ''', data=display_data)

@app.route('/decode-direct', methods=['POST'])
def decode_direct():
    global latest_payload
    signed_request = request.form.get('signed_request')

    print("📥 Received signed_request:", signed_request[:50] + "...")  # partial log for debug

    if not signed_request:
        return {"error": "Missing signed_request"}, 400

    decoded = decode_signed_request(signed_request, CONSUMER_SECRET)
    latest_payload = decoded
    print("✅ Decoded Payload:\n", json.dumps(decoded, indent=2))
    return {"status": "Decoded"}, 200

if __name__ == '__main__':
    app.run(debug=True)
