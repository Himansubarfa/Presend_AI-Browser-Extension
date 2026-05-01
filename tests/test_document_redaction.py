import requests, base64, sys, os, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://localhost:5000/scan/document"
if len(sys.argv) != 2:
    print("Usage: python test_document_redaction.py C:/Users/himan/OneDrive/Desktop/test.pdf")
    sys.exit(1)

file_path = sys.argv[1]
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    sys.exit(1)

print(f"Sending {file_path} ...")
with open(file_path, "rb") as f:
    response = requests.post(URL, files={"file": f}, verify=False)

data = response.json()
print(f"Status: {data.get('status')}")
print(f"Entities found: {len(data.get('entities', []))}")

b64 = data.get("redacted_file_base64")
if b64:
    b64 = b64.strip().replace("\n", "").replace(" ", "")
    b64 += "=" * ((4 - len(b64) % 4) % 4)
    out_name = data.get("redacted_filename", "redacted_output")
    with open(out_name, "wb") as out:
        out.write(base64.b64decode(b64))
    print(f"Redacted file saved to: {out_name}")