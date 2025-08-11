import requests, uuid, json, time
from dotenv import load_dotenv
import os

load_dotenv()

api_url = os.getenv("CLOVA_API_URL")
secret = os.getenv("CLOVA_SECRET_KEY")

image_path = r"C:\Users\jaemi\Documents\Project\iljjagom\test_code\ClovaOCR_test\sample.jpg"

headers = {"X-OCR-SECRET": secret}
payload = {
    "version": "V2",
    "requestId": str(uuid.uuid4()),
    "timestamp": int(time.time() * 1000),
    "images": [{"format": "jpg", "name": "sample"}]
}
files = [
    ("file", open(image_path, "rb")),
    ("message", (None, json.dumps(payload), "application/json"))
]

res = requests.post(api_url, headers=headers, files=files, timeout=30)

if res.status_code == 200:
    data = res.json()
    texts = []
    for image in data.get("images", []):
        for field in image.get("fields", []):
            texts.append(field.get("inferText", ""))
    print(" ".join(texts))
else:
    print("Request failed:", res.status_code, res.text)
