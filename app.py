import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv
from pathlib import Path

# Optional: auto-refresh (pip install streamlit-autorefresh)
try:
    from streamlit_autorefresh import st_autorefresh
    AUTORELOAD_AVAILABLE = True
except Exception:
    AUTORELOAD_AVAILABLE = False

# --- Load environment variables ---
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# --- Storage paths ---
FLASHCARD_DIR = Path("storage/flashcards")
QUIZ_DIR = Path("storage/quizzes")
FLASHCARD_DIR.mkdir(parents=True, exist_ok=True)
QUIZ_DIR.mkdir(parents=True, exist_ok=True)

# --- Page config ---
st.set_page_config(page_title="Study Buddy AI", layout="wide")

# --- Hide Streamlit menu, header, footer ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- CSS Styling ---
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

    .pomodoro-box {
        position: fixed;
        top: 70px;
        right: 20px;
        background: #ffffffee;
        border: 2px solid #4a90e2;
        border-radius: 12px;
        padding: 8px;
        width: 180px;
        font-size: 13px;
        text-align: center;
        box-shadow: 2px 6px 18px rgba(0,0,0,0.12);
        z-index: 1001;
    }
    </style>

    <!-- Clouds -->
    <div class="cloud" style="top:100px;"></div>
    <div class="cloud" style="top:300px;"></div>
    <div class="cloud" style="top:500px;"></div>
""", unsafe_allow_html=True)

# ----------------------
# Storage Helpers
# ----------------------
def save_to_file(base_dir, subject, topic, content):
    subject_dir = base_dir / subject
    subject_dir.mkdir(parents=True, exist_ok=True)
    file_path = subject_dir / f"{topic}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path

def list_subjects(base_dir):
    return [d.name for d in base_dir.iterdir() if d.is_dir()]

def list_topics(base_dir, subject):
    subject_dir = base_dir / subject
    if subject_dir.exists():
        return [f.stem for f in subject_dir.glob("*.md")]
    return []

def read_content(base_dir, subject, topic):
    file_path = base_dir / subject / f"{topic}.md"
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return "❌ No saved content found."

# ----------------------
# Pomodoro Session State
# ----------------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "show_pomodoro" not in st.session_state:
    st.session_state.show_pomodoro = False
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
# Autorefresh (live ticking)
# ----------------------
if AUTORELOAD_AVAILABLE and st.session_state.timer_running:
    st_autorefresh(interval=1000, limit=None, key="pomodoro_autorefresh")

# ----------------------
# Pomodoro Badge
# ----------------------
col_main, col_badge = st.columns([10, 1])
with col_badge:
    if st.button("🍅 Pomodoro"):
        if not st.session_state.timer_running:  
            st.session_state.show_pomodoro = not st.session_state.show_pomodoro

# ----------------------
# Pomodoro Settings Dropdown
# ----------------------
if st.session_state.show_pomodoro and not st.session_state.timer_running:
    st.markdown('<div class="pomodoro-box">', unsafe_allow_html=True)

    st.number_input("Work (min)", min_value=1, max_value=180,
                    value=st.session_state.work_time, key="work_time")
    st.number_input("Break (min)", min_value=1, max_value=60,
                    value=st.session_state.break_time, key="break_time")

    c1, c2 = st.columns(2)
    if c1.button("▶️ Start"):
        st.session_state.start_time = time.time()
        st.session_state.timer_running = True
        st.session_state.on_break = False
        st.session_state.show_pomodoro = False

    if c2.button("🔄 Reset"):
        st.session_state.timer_running = False
        st.session_state.start_time = None
        st.session_state.on_break = False
        st.session_state.show_pomodoro = False

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------
# Timer Display
# ----------------------
def format_mmss(seconds):
    if seconds < 0: seconds = 0
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

if st.session_state.timer_running:
    elapsed = int(time.time() - st.session_state.start_time)
    total = (st.session_state.break_time if st.session_state.on_break else st.session_state.work_time) * 60
    remaining = total - elapsed

    if remaining <= 0:
        if not st.session_state.on_break:
            st.success("🎉 Work done! Break time.")
            st.session_state.on_break = True
        else:
            st.success("✅ Break over! Back to work.")
            st.session_state.on_break = False
        st.session_state.start_time = time.time()
        remaining = (st.session_state.break_time if st.session_state.on_break else st.session_state.work_time) * 60

    st.markdown(
        f"""
        <div class="pomodoro-box">
            <div style="font-weight:700; font-size:15px;">{"Break" if st.session_state.on_break else "Work"}</div>
            <div style="font-size:18px; margin-top:6px;">⏰ {format_mmss(remaining)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("🛑 Stop Pomodoro", key="stop_pom"):
        st.session_state.timer_running = False
        st.session_state.start_time = None
        st.session_state.on_break = False

# ----------------------
# Navigation Helpers
# ----------------------
def go_to(page):
    st.session_state.page = page

def back_button():
    st.button("⬅️ Back to Home", on_click=go_to, args=("welcome",))

# ----------------------
# Pages
# ----------------------
if st.session_state.page == "welcome":
    st.markdown('<h1 style="text-align:center;">🐰 Study Buddy AI 🌸</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align:center; color:#34495e;">Your cute and smart study companion!</h3>', unsafe_allow_html=True)

    st.write("----")
    st.write("✨ **What you can do:**")
    st.write("📚 Flashcards – Generate and save flashcards")
    st.write("🧠 Quiz – Generate and save quizzes")
    st.write("🤖 Chatbot – Ask me anything")

    c1, c2, c3 = st.columns(3)
    with c1: st.button("📚 Flashcards", on_click=go_to, args=("flashcards",))
    with c2: st.button("🧠 Quiz", on_click=go_to, args=("quiz",))
    with c3: st.button("🤖 Chatbot", on_click=go_to, args=("chatbot",))

# --- Flashcards Page ---
elif st.session_state.page == "flashcards":
    st.header("📚 Flashcards")
    subject = st.text_input("Enter Subject:")
    topic = st.text_input("Enter Topic:")
    if st.button("Generate Flashcards"):
        if subject and topic and api_key:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {"model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": f"Make 5 flashcards about {topic}"}]}
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                st.write(content)
                save_to_file(FLASHCARD_DIR, subject, topic, content)
                st.success(f"✅ Saved under {subject}/{topic}")
            else:
                st.error("❌ Failed to generate flashcards.")
        else:
            st.warning("⚠️ Enter subject, topic, and check API key.")

    # --- Show saved flashcards ---
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
        st.info("No flashcards saved yet.")
    back_button()

# --- Quiz Page ---
elif st.session_state.page == "quiz":
    st.header("🧠 Quiz Mode")
    subject = st.text_input("Enter Subject (Quiz):")
    topic = st.text_input("Enter Topic (Quiz):")
    text = st.text_area("Paste study material:")
    if st.button("Generate Quiz"):
        if subject and topic and text and api_key:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {"model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": f"Make a quiz with answers from this: {text}"}]}
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                st.write(content)
                save_to_file(QUIZ_DIR, subject, topic, content)
                st.success(f"✅ Saved under {subject}/{topic}")
            else:
                st.error("❌ Failed to generate quiz.")
        else:
            st.warning("⚠️ Enter subject, topic, material, and check API key.")

    # --- Show saved quizzes ---
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
        st.info("No quizzes saved yet.")
    back_button()

# --- Chatbot Page ---
elif st.session_state.page == "chatbot":
    st.header("🤖 Chatbot")
    user_input = st.text_input("Ask me anything:")
    if st.button("Send"):
        if user_input and api_key:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {"model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": user_input}]}
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 200:
                st.write(resp.json()["choices"][0]["message"]["content"])
            else:
                st.error("❌ Failed to get chatbot response.")
        else:
            st.warning("⚠️ Enter text and check API key.")
    back_button()






