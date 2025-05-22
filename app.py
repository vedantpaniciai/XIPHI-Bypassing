from flask import Flask, request, render_template_string
import base64
import json
import hmac
import hashlib
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Constants
CONSUMER_SECRET = 'FFE6251BCA3AFB6A3301E39F43597EC67439F8C58EE5F74A0992F40CEA1DC17D'
SALESFORCE_CANVAS_APP_URL = "https://your-salesforce-instance.lightning.force.com/lightning/n/FastApp"  # 👈 Update this!

app = Flask(__name__)

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

def extract_signed_request_from_salesforce():
    # Headless browser setup
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        print("Opening Salesforce Canvas App...")
        driver.get(SALESFORCE_CANVAS_APP_URL)
        time.sleep(8)  # Adjust depending on Salesforce load time

        print("Extracting signedRequest...")
        signed_request = driver.execute_script("return Sfdc.canvas.context().signedRequest")

        if signed_request:
            print("Signed request found ✅")
            return signed_request
        else:
            print("⚠️ signedRequest not found.")
            return None
    except Exception as e:
        print("Error with Selenium:", e)
        return None
    finally:
        driver.quit()

@app.route('/')
def home():
    signed_request = extract_signed_request_from_salesforce()

    if not signed_request:
        display_data = "❌ Failed to extract signedRequest from Salesforce Canvas."
    else:
        decoded = decode_signed_request(signed_request, CONSUMER_SECRET)
        display_data = json.dumps(decoded, indent=2)

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Salesforce Canvas Payload Viewer</title>
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

if __name__ == '__main__':
    app.run(debug=True)
