import requests
import base64
import json
import os
import sys

# =====================================================
# CONFIG
# =====================================================

FLOW_URL = "https://2d4fe8251353e16bb99d35aef02f08.4e.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/81dd621591ba40408d390b20dedeb9a1/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=_WG-Dhz7G8Sk-zIE6U1kZzmzbnxEL1FO0kE0v2R93Eo"

# =====================================================
# READ FILE FROM CLI ARGUMENT
# =====================================================

if len(sys.argv) < 2:
    print("❌ ERROR: Please provide a PDF file path.")
    print("✅ Usage: python trigger_flow.py <file_path>")
    sys.exit(1)

FILE_PATH = sys.argv[1]

# =====================================================
# VALIDATION
# =====================================================

if not os.path.exists(FILE_PATH):
    print(" ERROR: File not found:", FILE_PATH)
    sys.exit(1)

allowed_extensions = (".pdf", ".png", ".jpg", ".jpeg", ".tiff")
if not FILE_PATH.lower().endswith(allowed_extensions):
    print(" ERROR: Invalid file type. Only PDF/JPG/PNG/TIFF allowed.")
    sys.exit(1)

# =====================================================
# READ FILE AS BINARY
# =====================================================

with open(FILE_PATH, "rb") as f:
    file_bytes = f.read()

if len(file_bytes) == 0:
    print(" ERROR: File is empty (0 bytes).")
    sys.exit(1)

# =====================================================
# CONVERT TO BASE64
# =====================================================

file_base64 = base64.b64encode(file_bytes).decode("utf-8")

# =====================================================
# BUILD PAYLOAD
# =====================================================

payload = {
    "fileName": os.path.basename(FILE_PATH),
    "fileContent": file_base64
}

headers = {
    "Content-Type": "application/json"
}

# =====================================================
# SEND TO POWER AUTOMATE
# =====================================================

try:
    response = requests.post(
        FLOW_URL,
        data=json.dumps(payload),
        headers=headers,
        timeout=300
    )

   # print("\n HTTP Status Code:", response.status_code)
# Try to convert numeric response like 24080155.0 → 24080155

    body = response.text.strip()

    if body.replace('.', '', 1).isdigit():
        print(int(float(body)))
    else:
        print(" Response Body:\n", body)

except Exception:
    print(" Response Body:\n", response.text)


except requests.exceptions.Timeout:
    print(" ERROR: Request timed out.")

except requests.exceptions.ConnectionError:
    print(" ERROR: Network connection failed.")

except Exception as e:
    print(" ERROR:", str(e))
