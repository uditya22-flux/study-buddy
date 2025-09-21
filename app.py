import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv

# Optional: auto-refresh (pip install streamlit-autorefresh)
try:
    from streamlit_autorefresh import st_autorefresh
    AUTORELOAD_AVAILABLE = True
except Exception:
    AUTORELOAD_AVAILABLE = False

# --- Load environment variables ---
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

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
# Badge Button
# ----------------------
col_main, col_badge = st.columns([10, 1])
with col_badge:
    if st.button("🍅 Pomodoro"):
        if not st.session_state.timer_running:  # only toggle if not running
            st.session_state.show_pomodoro = not st.session_state.show_pomodoro

# ----------------------
# Settings Dropdown
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
        st.session_state.show_pomodoro = False  # 🔴 Hide dropdown immediately

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
# Helpers
# ----------------------
def play_sound(sound_url):
    st.markdown(f"""
        <audio autoplay>
            <source src="{sound_url}" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)

def go_to(page, sound_url=None):
    st.session_state.page = page
    if sound_url:
        st.session_state.sound_url = sound_url

def back_button():
    st.button("⬅️ Back to Home",
              on_click=go_to,
              args=("welcome", "https://actions.google.com/sounds/v1/cartoon/pop.ogg"))

# ----------------------
# Pages
# ----------------------
if "sound_url" in st.session_state:
    play_sound(st.session_state.sound_url)
    del st.session_state["sound_url"]

if st.session_state.page == "welcome":
    st.markdown('<h1 style="text-align:center;">🐰 Study Buddy AI 🌸</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align:center; color:#34495e;">Your cute and smart study companion!</h3>', unsafe_allow_html=True)

    st.write("----")
    st.write("✨ **What you can do:**")
    st.write("📚 Flashcards – Generate flashcards for your topics")
    st.write("🧠 Quiz – Turn text into quiz questions")
    st.write("🤖 Chatbot – Ask me anything")

    c1, c2, c3 = st.columns(3)
    with c1: st.button("📚 Flashcards", on_click=go_to, args=("flashcards",))
    with c2: st.button("🧠 Quiz", on_click=go_to, args=("quiz",))
    with c3: st.button("🤖 Chatbot", on_click=go_to, args=("chatbot",))

elif st.session_state.page == "flashcards":
    st.header("📚 Flashcards")
    topic = st.text_input("Enter a topic:")
    if st.button("Generate Flashcards"):
        if topic and api_key:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {"model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": f"Make 5 flashcards about {topic}"}]}
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 200:
                st.write(resp.json()["choices"][0]["message"]["content"])
            else:
                st.error("❌ Failed to generate flashcards.")
        else:
            st.warning("⚠️ Enter a topic and check API key.")
    back_button()

elif st.session_state.page == "quiz":
    st.header("🧠 Quiz Mode")
    text = st.text_area("Paste study material:")
    if st.button("Generate Quiz"):
        if text and api_key:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {"model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": f"Make a quiz with answers from this: {text}"}]}
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 200:
                st.write(resp.json()["choices"][0]["message"]["content"])
            else:
                st.error("❌ Failed to generate quiz.")
        else:
            st.warning("⚠️ Paste study text and check API key.")
    back_button()

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





