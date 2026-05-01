# tests/test_image_redaction.py
import requests
import base64
import sys
import os

# Disable SSL warnings for self-signed cert
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://localhost:5000/scan/image"

if len(sys.argv) != 2:
    print("Usage: python test_image_redaction.py C:/Users/himan/OneDrive/Desktop/Gemini_Generated_Image_zfaf6czfaf6czfaf.jpg")
    sys.exit(1)

image_path = sys.argv[1]
if not os.path.exists(image_path):
    print(f"File not found: {image_path}")
    sys.exit(1)

print(f"Sending {image_path} ...")
with open(image_path, "rb") as f:
    response = requests.post(URL, files={"image": f}, verify=False)

if response.status_code != 200:
    print(f"Error {response.status_code}: {response.text}")
    sys.exit(1)

data = response.json()
print(f"Status: {data.get('status')}")
print(f"Entities found: {len(data.get('entities', []))}")
for ent in data.get("entities", []):
    print(f"  {ent['label']}: '{ent['text']}'")

b64 = data.get("redacted_image_base64")
if b64:
    # Ensure padding
    b64 = b64.strip().replace("\n", "").replace(" ", "")
    b64 += "=" * ((4 - len(b64) % 4) % 4)
    with open("redacted.jpg", "wb") as out:
        out.write(base64.b64decode(b64))
    print("\nRedacted image saved to: redacted.jpg")
else:
    print("No redacted image returned.")