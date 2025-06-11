import requests

response = requests.post(
    "http://127.0.0.1:5000/extract-text",
    json={
        "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    }
)

print("Status:", response.status_code)
print("Response:", response.json())
