# test_chat.py
from dotenv import load_dotenv
import os, requests, json

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("API key not found. Check that .env exists and has OPENROUTER_API_KEY.")
    raise SystemExit(1)

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "gpt-4o-mini",        # change if your account uses a different model
    "messages": [{"role": "user", "content": "Hello chatbot"}]
}

resp = requests.post(url, headers=headers, json=payload)
if resp.status_code != 200:
    print("Request failed:", resp.status_code, resp.text)
else:
    data = resp.json()
    # Attempt to extract the reply safely
    try:
        reply = data["choices"][0]["message"]["content"]
    except Exception:
        reply = json.dumps(data, indent=2)
    print("Bot reply:\n", reply)


