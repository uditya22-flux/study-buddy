# chatbot.py
from dotenv import load_dotenv
import os, requests, time

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("❌ OPENROUTER_API_KEY not found in .env. Add it and try again.")
    exit(1)

URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def ask_chatbot(messages):
    """Send conversation 'messages' to the API and return assistant reply text."""
    payload = {
        "model": "gpt-4o-mini",   # you can change this if needed
        "messages": messages
    }

    r = None
    try:
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        # safe extraction of the assistant reply
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print("Network/API error:", e)
        if r is not None:
            print("Status code:", r.status_code)
            try:
                print("Response body:", r.text)
            except Exception:
                pass
        return "⚠️ Sorry — I couldn't reach the API right now."
    except Exception as e:
        print("Unexpected error parsing response:", e)
        return "⚠️ Sorry — something went wrong."

def main():
    # system message defines personality/role
    messages = [{"role": "system", "content": "You are a helpful, friendly study buddy."}]

    print("🤖 Chatbot ready. Type messages and press Enter. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # add user message, ask API, print assistant reply, store assistant reply
        messages.append({"role": "user", "content": user_input})
        reply = ask_chatbot(messages)
        print("Bot:", reply, "\n")
        messages.append({"role": "assistant", "content": reply})

        # optional: keep conversation from growing too large (trim older messages)
        if len(messages) > 30:    # adjustable
            # preserve system message and last 20 messages
            messages = [messages[0]] + messages[-20:]

if __name__ == "__main__":
    main()
