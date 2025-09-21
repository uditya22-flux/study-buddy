# app.py
import streamlit as st
import requests
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# ----------------------
# Setup & Config
# ----------------------
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    st.error("❌ OPENROUTER_API_KEY missing in .env file.")
    st.stop()

URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Storage folders
FLASHCARD_DIR = Path("storage/flashcards")
QUIZ_DIR = Path("storage/quizzes")
FLASHCARD_DIR.mkdir(parents=True, exist_ok=True)
QUIZ_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Study Buddy AI", layout="wide")

# ----------------------
# CSS Styling
# ----------------------
st.markdown("""
    <style>
     .stApp {
        background: linear-gradient(135deg, #a2d4f4 0%, #b5e3ff 50%, #dff6ff 100%);
        background-attachment: fixed;
        font-family: "Comic Sans MS", cursive, sans-serif;
        color: #1a3c6e;
    }
    div.stButton > button {
        background-color: #4a90e2;
        color: white !important;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        padding: 10px 18px;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.15);
        transition: all 0.18s ease;
    }
    div.stButton > button:hover {
        background-color: #357ab7;
        transform: scale(1.03);
    }
    .cloud {
        position: absolute;
        width: 180px;
        height: 100px;
        background: #fff;
        border-radius: 50%;
        opacity: 0.95;
        animation: float 60s linear infinite;
        box-shadow: 8px 10px 30px rgba(0,0,0,0.04);
    }
    .cloud:before, .cloud:after {
        content: '';
        position: absolute;
        background: #fff;
        border-radius: 50%;
    }
    .cloud:before { width: 100px; height: 100px; top: -40px; left: 20px; }
    .cloud:after { width: 120px; height: 120px; top: -50px; right: 15px; }
    @keyframes float { 0% { left: -250px; } 100% { left: 100%; } }
    </style>

    <!-- Clouds -->
    <div class="cloud" style="top:100px;"></div>
    <div class="cloud" style="top:300px;"></div>
    <div class="cloud" style="top:500px;"></div>
""", unsafe_allow_html=True)

# ----------------------
# Helpers
# ----------------------
def ask_chatbot(messages):
    """Send messages to OpenRouter API."""
    payload = {"model": "gpt-4o-mini", "messages": messages}
    try:
        r = requests.post(URL, headers=HEADERS, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ API Error: {e}"

def save_to_file(base_dir, subject, topic, content):
    subject_dir = base_dir / subject
    subject_dir.mkdir(parents=True, exist_ok=True)
    file_path = subject_dir / f"{topic}.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path

def list_subjects(base_dir):
    return [d.name for d in base_dir.iterdir() if d.is_dir()]

def list_topics(base_dir, subject):
    subject_dir = base_dir / subject
    return [f.stem for f in subject_dir.glob("*.md")] if subject_dir.exists() else []

def read_content(base_dir, subject, topic):
    file_path = base_dir / subject / f"{topic}.md"
    return file_path.read_text(encoding="utf-8") if file_path.exists() else "❌ No saved content."

def format_mmss(seconds):
    m, s = divmod(max(0, int(seconds)), 60)
    return f"{m:02d}:{s:02d}"

# ----------------------
# Session State
# ----------------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful, friendly study buddy."}]
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "work_time" not in st.session_state:
    st.session_state.work_time = 25
if "break_time" not in st.session_state:
    st.session_state.break_time = 5
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "on_break" not in st.session_state:
    st.session_state.on_break = False

# ----------------------
# Navigation
# ----------------------
def go_to(page): st.session_state.page = page
def back_button(): st.button("⬅️ Back to Home", on_click=go_to, args=("welcome",))

# ----------------------
# Welcome Page
# ----------------------
if st.session_state.page == "welcome":
    st.title("🐰 Study Buddy AI 🌸")
    st.subheader("Your all-in-one study companion!")

    st.write("✨ Features:")
    st.write("- 📚 Flashcards (save by subject/topic)")
    st.write("- 🧠 Quiz mode (save by subject/topic)")
    st.write("- ⏳ Pomodoro timer")
    st.write("- 🤖 Chatbot with memory")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.button("📚 Flashcards", on_click=go_to, args=("flashcards",))
    with c2: st.button("🧠 Quiz", on_click=go_to, args=("quiz",))
    with c3: st.button("🤖 Chatbot", on_click=go_to, args=("chatbot",))
    with c4: st.button("⏳ Pomodoro", on_click=go_to, args=("pomodoro",))

# ----------------------
# Flashcards Page
# ----------------------
elif st.session_state.page == "flashcards":
    st.header("📚 Flashcards")
    subject = st.text_input("Enter Subject:")
    topic = st.text_input("Enter Topic:")
    if st.button("Generate Flashcards"):
        if subject and topic:
            resp = ask_chatbot([{"role": "user", "content": f"Make 5 flashcards about {topic}"}])
            st.markdown(resp)
            save_to_file(FLASHCARD_DIR, subject, topic, resp)
            st.success(f"✅ Saved under {subject}/{topic}")
        else:
            st.warning("⚠️ Enter subject and topic.")
    st.subheader("📂 Your Saved Flashcards")
    subjects = list_subjects(FLASHCARD_DIR)
    if subjects:
        sel_subject = st.selectbox("Choose Subject", subjects)
        topics = list_topics(FLASHCARD_DIR, sel_subject)
        if topics:
            sel_topic = st.selectbox("Choose Topic", topics)
            if st.button("📖 View Flashcards"):
                st.markdown(read_content(FLASHCARD_DIR, sel_subject, sel_topic))
    else:
        st.info("No flashcards yet.")
    back_button()

# ----------------------
# Quiz Page
# ----------------------
elif st.session_state.page == "quiz":
    st.header("🧠 Quiz Mode")
    subject = st.text_input("Enter Subject (Quiz):")
    topic = st.text_input("Enter Topic (Quiz):")
    text = st.text_area("Paste study material:")
    if st.button("Generate Quiz"):
        if subject and topic and text:
            resp = ask_chatbot([{"role": "user", "content": f"Make a quiz with answers from this: {text}"}])
            st.markdown(resp)
            save_to_file(QUIZ_DIR, subject, topic, resp)
            st.success(f"✅ Saved under {subject}/{topic}")
        else:
            st.warning("⚠️ Enter subject, topic, and material.")
    st.subheader("📂 Your Saved Quizzes")
    subjects = list_subjects(QUIZ_DIR)
    if subjects:
        sel_subject = st.selectbox("Choose Subject", subjects)
        topics = list_topics(QUIZ_DIR, sel_subject)
        if topics:
            sel_topic = st.selectbox("Choose Topic", topics)
            if st.button("📖 View Quiz"):
                st.markdown(read_content(QUIZ_DIR, sel_subject, sel_topic))
    else:
        st.info("No quizzes yet.")
    back_button()

# ----------------------
# Chatbot Page
# ----------------------
elif st.session_state.page == "chatbot":
    st.header("🤖 Study Buddy Chatbot")
    # Display history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"): st.write(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"): st.write(msg["content"])
    # User input
    if user_input := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.write(user_input)
        reply = ask_chatbot(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"): st.write(reply)
    back_button()

# ----------------------
# Pomodoro Page
# ----------------------
elif st.session_state.page == "pomodoro":
    st.header("⏳ Pomodoro Timer")
    st.number_input("Work (min)", 1, 180, value=st.session_state.work_time, key="work_time")
    st.number_input("Break (min)", 1, 60, value=st.session_state.break_time, key="break_time")

    if not st.session_state.timer_running:
        if st.button("▶️ Start"):
            st.session_state.start_time = time.time()
            st.session_state.timer_running = True
            st.session_state.on_break = False
    else:
        elapsed = int(time.time() - st.session_state.start_time)
        total = (st.session_state.break_time if st.session_state.on_break else st.session_state.work_time) * 60
        remaining = total - elapsed
        if remaining <= 0:
            st.session_state.on_break = not st.session_state.on_break
            st.session_state.start_time = time.time()
            remaining = (st.session_state.break_time if st.session_state.on_break else st.session_state.work_time) * 60
            st.balloons()
        st.write("⏰", "Break" if st.session_state.on_break else "Work", format_mmss(remaining))
        if st.button("🛑 Stop"):
            st.session_state.timer_running = False
            st.session_state.start_time = None
            st.session_state.on_break = False
    back_button()







