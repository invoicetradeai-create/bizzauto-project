import google.generativeai as genai
import os

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Skipping test: GEMINI_API_KEY not set")
    exit(0)

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("Successfully instantiated gemini-2.5-flash")
    # Try to generate content to be sure
    response = model.generate_content("Hello")
    print("Successfully generated content")
except Exception as e:
    print(f"Failed to use gemini-2.5-flash: {e}")

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Successfully instantiated gemini-1.5-flash")
except Exception as e:
    print(f"Failed to use gemini-1.5-flash: {e}")
