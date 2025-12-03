import requests
import json

BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/meta_whatsapp/send-meta-whatsapp"

def test_request(headers, description):
    print(f"--- Testing {description} ---")
    try:
        response = requests.post(
            f"{BASE_URL}{ENDPOINT}",
            json={"to": "1234567890", "message_data": "test"},
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

if __name__ == "__main__":
    # Test 1: No Authorization Header
    test_request({}, "No Authorization Header")

    # Test 2: Invalid Authorization Header
    test_request({"Authorization": "Bearer invalid_token"}, "Invalid Authorization Header")
