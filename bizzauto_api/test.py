import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key_env = os.getenv("OPENAI_API_KEY")

if not gemini_api_key and not openai_api_key_env:
    print("Neither GEMINI_API_KEY nor OPENAI_API_KEY environment variables are set.")
    print("Please ensure your .env file is in bizzauto_api/ and contains these keys.")
    print("Or check if load_dotenv() is working as expected.")
else:
    key_to_use = gemini_api_key if gemini_api_key else openai_api_key_env
    key_name = "GEMINI_API_KEY" if gemini_api_key else "OPENAI_API_KEY"
    print(f"Using {key_name}: {key_to_use[:5]}...{key_to_use[-5:]}")

try:
    client = OpenAI(
        api_key=key_to_use,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    chat_completion = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[{"role": "user", "content": "Hello, how are you?"}],
        max_tokens=10
    )

    print("\nSuccessfully connected to Gemini API!")
    print("Response:", chat_completion.choices[0].message.content)
except Exception as e:
    print(f"\nError connecting to Gemini API: {e}")
    print("Your API key might be incorrect or have issues.")