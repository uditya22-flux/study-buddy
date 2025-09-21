import os, requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

url = "https://api.openrouter.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
data = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}]
}

r = requests.post(url, headers=headers, json=data)
print("Status:", r.status_code)
print("Response:", r.json())
