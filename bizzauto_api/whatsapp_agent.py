from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_whatsapp_agent(message: str) -> dict:
    """WhatsApp agent using direct OpenAI API"""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful WhatsApp assistant."},
                {"role": "user", "content": message}
            ]
        )
        return {
            "response": response.choices[0].message.content,
            "status": "success"
        }
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "status": "error"
        }

