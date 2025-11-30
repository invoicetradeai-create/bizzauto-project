import requests
import os
from dotenv import load_dotenv

# Load env to get token if possible, or just test public/protected
# Assuming we need a token. I'll try to hit it without token first to see if we get 401 (which means network is OK)
# or if we get connection error.

API_URL = "http://127.0.0.1:8000/api/clients"

def test_clients_endpoint():
    try:
        print(f"Testing {API_URL}...")
        response = requests.get(API_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except requests.exceptions.ConnectionError:
        print("Connection Error: Could not connect to backend.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_clients_endpoint()
