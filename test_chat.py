from dotenv import load_dotenv
import os, requests

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("❌ API key not found. Please create a .env file with:")
    print("OPENROUTER_API_KEY=your_api_key_here")
    exit()

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello chatbot"}]
}

try:
    resp = requests.post(url, headers=headers, json=data, timeout=20)
    print("Status:", resp.status_code)
    if resp.status_code == 200:
        print("✅ Response:", resp.json()["choices"][0]["message"]["content"])
    else:
        print("❌ Error:", resp.text)
except Exception as e:
    print("⚠️ Exception:", e)


