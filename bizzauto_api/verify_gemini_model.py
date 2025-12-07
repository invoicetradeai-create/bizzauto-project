from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not found in environment variables.")
    exit(1)

print(f"Found API Key: {api_key[:5]}...{api_key[-5:]}")

genai.configure(api_key=api_key)

try:
    print("Attempting to initialize gemini-2.0-flash...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    print("Sending test prompt...")
    response = model.generate_content("Hello, just checking if you are active. Reply with 'Yes, I am active'.")
    
    print(f"Success! Response: {response.text}")

except Exception as e:
    print(f"Error: {e}")
    # Print available models if 404
    if "404" in str(e):
        print("Listing available 'flash' models:")
        for m in genai.list_models():
            if 'flash' in m.name:
                print(m.name)
