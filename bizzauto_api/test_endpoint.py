import requests

url = "http://127.0.0.1:8000/api/meta_whatsapp/send-meta-whatsapp"
print(f"Testing URL: {url}")

try:
    response = requests.post(url, json={})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
