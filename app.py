import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Page config
st.set_page_config(page_title="Study Buddy AI", layout="wide")

# --- Custom CSS for aesthetic style ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(to bottom, #a7d8f0, #ffffff);
    }
    .icon-button {
        font-size: 50px;
        text-align: center;
        cursor: pointer;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Function to play sound ---
def play_sound(sound_url):
    sound_html = f"""
    <audio autoplay>
        <source src="{sound_url}" type="audio/mpeg">
    </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# --- App Navigation ---
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# --- Welcome Page ---
if st.session_state.page == "welcome":
    st.title("🐰 Welcome to Study Buddy AI 🌸")
    st.write("Choose what you’d like to do today:")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📚 Flashcards"):
            play_sound("https://actions.google.com/sounds/v1/cartoon/pop.ogg")
            st.session_state.page = "flashcards"

    with col2:
        if st.button("🧠 Quiz"):
            play_sound("https://actions.google.com/sounds/v1/cartoon/slide_whistle_to_drum_hit.ogg")
            st.session_state.page = "quiz"

    with col3:
        if st.button("🤖 Chatbot"):
            play_sound("https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg")
            st.session_state.page = "chatbot"

# --- Flashcards Page ---
elif st.session_state.page == "flashcards":
    st.header("📚 Flashcards")
    topic = st.text_input("Enter a topic to generate flashcards:")
    if st.button("Generate Flashcards"):
        play_sound("https://actions.google.com/sounds/v1/cartoon/boing.ogg")
        if topic and api_key:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": f"Make 5 flashcards about {topic}"}]
            }
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 200:
                st.write(resp.json()["choices"][0]["message"]["content"])
            else:
                st.error("Failed to generate flashcards.")
        else:
            st.warning("Please enter a topic and ensure API key is set.")
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "welcome"

# --- Quiz Page ---
elif st.session_state.page == "quiz":
    st.header("🧠 Quiz Mode")
    st.write("Enter text or a paragraph, and I’ll create quiz questions for you.")
    text = st.text_area("Paste study material here:")
    if st.button("Generate Quiz"):
        play_sound("https://actions.google.com/sounds/v1/cartoon/concussive_drum_hit.ogg")
        if text and api_key:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": f"Make a quiz with answers from this: {text}"}]
            }
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 200:
                st.write(resp.json()["choices"][0]["message"]["content"])
            else:
                st.error("Failed to generate quiz.")
        else:
            st.warning("Please enter study material and ensure API key is set.")
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "welcome"

# --- Chatbot Page ---
elif st.session_state.page == "chatbot":
    st.header("🤖 Chatbot")
    user_input = st.text_input("Ask me anything:")
    if st.button("Send"):
        play_sound("https://actions.google.com/sounds/v1/cartoon/jump.ogg")
        if user_input and api_key:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": user_input}]
            }
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 200:
                st.write(resp.json()["choices"][0]["message"]["content"])
            else:
                st.error("Failed to get chatbot response.")
        else:
            st.warning("Please type something and ensure API key is set.")
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "welcome"






