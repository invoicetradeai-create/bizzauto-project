import requests
import json

url = "http://127.0.0.1:8000/api/meta_whatsapp/webhook"

payload = {
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "123456789",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "1234567890",
              "phone_number_id": "1234567890"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Test User"
                },
                "wa_id": "1234567890"
              }
            ],
            "messages": [
              {
                "from": "1234567890",
                "id": "wamid.HBgLMTIzNDU2Nzg5MAUCABEYEjEyMzQ1Njc4OTAxMjM0NTY3AA==",
                "timestamp": "1678901234",
                "text": {
                  "body": "Hello World"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
