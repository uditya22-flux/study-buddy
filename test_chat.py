from dotenv import load_dotenv
import os, requests

# Load API key from .env
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Debug print
print("API Key found?", bool(api_key))

if not api_key:
    print("❌ API key not found. Did you create .env?")
    exit()

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
data = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello chatbot"}]
}

resp = requests.post(url, headers=headers, json=data)
print("Status:", resp.status_code)
print("Response:", resp.json())

