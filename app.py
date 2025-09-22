import streamlit as st
from dotenv import load_dotenv
import os, requests

# Load API key
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    st.error("❌ API key not found. Did you create a .env file?")
    st.stop()

url = "https://api.openrouter.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

# Session state to store chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful study buddy. Explain clearly and give examples."}
    ]

st.title("📚 Study Buddy Chatbot 🤖")

# Display past messages in chat bubbles
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div style='background:#DCF8C6; padding:8px; border-radius:10px; margin:5px 0;'><b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f"<div style='background:#ECECEC; padding:8px; border-radius:10px; margin:5px 0;'><b>Bot:</b> {msg['content']}</div>", unsafe_allow_html=True)

# Input box for new message
user_input = st.text_input("Type your message:")

if st.button("Send") and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Send request to API
    data = {"model": "gpt-4o-mini", "messages": st.session_state.messages}
    resp = requests.post(url, headers=headers, json=data)
    reply = resp.json()["choices"][0]["message"]["content"]

    # Add assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})

    st.rerun()

# Save chat history button
if st.button("💾 Save Chat"):
    with open("chat_history.txt", "w", encoding="utf-8") as f:
        for msg in st.session_state.messages:
            f.write(f"{msg['role']}: {msg['content']}\n")
    st.success("Chat saved to chat_history.txt ✅")

