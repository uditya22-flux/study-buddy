import streamlit as st
from dotenv import load_dotenv
import os, requests, random

# -------------------- Setup --------------------
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

st.set_page_config(page_title="Study Buddy AI 🤖", page_icon="📚", layout="wide")

# -------------------- Gradient Backgrounds --------------------
gradients = {
    "Welcome": "linear-gradient(to bottom, #fbc2eb, #a6c1ee)",   # pink-purple
    "Chat": "linear-gradient(to bottom, #ffdde1, #ee9ca7)",      # pink-peach
    "Flashcards": "linear-gradient(to bottom, #d4fc79, #96e6a1)",# mint green
    "Quizzes": "linear-gradient(to bottom, #a1c4fd, #c2e9fb)"    # sky blue
}

# -------------------- Initialize Session State --------------------
if "page" not in st.session_state:
    st.session_state.page = "Welcome"

# -------------------- Apply Gradient --------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {gradients[st.session_state.page]};
        background-attachment: fixed;
    }}
    .menu-btn {{
        display: inline-block;
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin: 20px;
        text-align: center;
        font-size: 22px;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.2);
        cursor: pointer;
        transition: transform 0.2s;
    }}
    .menu-btn:hover {{
        transform: scale(1.05);
        background: #ffe6f0;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- Fonts --------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&family=Baloo+2:wght@600&family=Shadows+Into+Light&display=swap');
    .welcome-title { font-family: 'Baloo 2', cursive; font-size: 40px; color: #ff6699; text-align:center; }
    .chat-title { font-family: 'Baloo 2', cursive; font-size: 34px; color: #ff6699; }
    .flash-title { font-family: 'Shadows Into Light', cursive; font-size: 34px; color: #ff9966; }
    .quiz-title { font-family: 'Comic Neue', cursive; font-size: 34px; color: #3366cc; }
    .chat-bubble-user { background: #ffd6e0; padding: 14px; border-radius: 20px; margin: 10px; }
    .chat-bubble-bot { background: #d6f0ff; padding: 14px; border-radius: 20px; margin: 10px; }
    </style>
""", unsafe_allow_html=True)

# -------------------- Welcome Page --------------------
if st.session_state.page == "Welcome":
    st.markdown("<h1 class='welcome-title'>🤖 Welcome to Study Buddy AI 🌸</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#333;'>Your cute AI-powered study companion ✨ Learn, Revise & Play 🎮</h3>", unsafe_allow_html=True)
    st.write("")

    # Motivational quote
    quotes = [
        "🌸 Every small step takes you closer to your goal!",
        "📚 Study a little every day and you’ll bloom like spring!",
        "💡 Knowledge grows when you share and revise!"
    ]
    st.info(random.choice(quotes))

    st.write("### 🌟 What can you do here?")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 💬 Chat with Buddy AI")
        st.write("Ask questions, get help, and chat with your friendly Study Buddy 🤖")
        if st.button("➡️ Start Chat"):
            st.session_state.page = "Chat"
            st.rerun()

    with col2:
        st.markdown("### 🎴 Flashcards")
        st.write("Generate or create flashcards to revise topics quickly 🌸")
        if st.button("➡️ Flashcards"):
            st.session_state.page = "Flashcards"
            st.rerun()

    with col3:
        st.markdown("### 📝 Quizzes")
        st.write("Turn your notes into fun quiz games 🎮 and earn rewards 🎊")
        if st.button("➡️ Quizzes"):
            st.session_state.page = "Quizzes"
            st.rerun()

    st.write("---")
    st.markdown("<p style='text-align:center; color:#444;'>Made with 💖 by Study Buddy AI</p>", unsafe_allow_html=True)

# -------------------- Chat Page --------------------
if st.session_state.page == "Chat":
    st.markdown("<h1 class='chat-title'>💬 Study Buddy AI Chat</h1>", unsafe_allow_html=True)

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "system", "content": "You are a friendly study buddy AI. Be playful, helpful, and use emojis 🌸🤖."}
        ]

    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-bubble-user'>🙋‍♀️ {msg['content']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            st.markdown(f"<div class='chat-bubble-bot'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

    user_input = st.text_input("Type your message 🤖:")
    if st.button("✨ Send") and user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        data = {"model": "gpt-4o-mini", "messages": st.session_state.chat_messages}
        reply = requests.post(url, headers=headers, json=data).json()["choices"][0]["message"]["content"]
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.button("🏠 Back to Home"):
        st.session_state.page = "Welcome"
        st.rerun()

# -------------------- Flashcards Page --------------------
if st.session_state.page == "Flashcards":
    st.markdown("<h1 class='flash-title'>🎴 Study Buddy AI Flashcards</h1>", unsafe_allow_html=True)

    topic = st.text_input("Enter a topic for flashcards 🌸")
    if st.button("🌼 Generate Flashcards"):
        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role":"user","content":f"Make 5 flashcards about {topic}. Format: Q - A"}]
        }
        reply = requests.post(url, headers=headers, json=data).json()["choices"][0]["message"]["content"]

        for line in reply.split("\n"):
            if "-" in line:
                q, a = line.split("-", 1)
                with st.expander(f"❓ {q.strip()}"):
                    st.write(f"✅ {a.strip()}")

        os.makedirs("flashcards", exist_ok=True)
        with open(f"flashcards/{topic}.txt", "w", encoding="utf-8") as f:
            f.write(reply)
        st.success(f"Flashcards saved in flashcards/{topic}.txt 🌸")

    q = st.text_input("Custom Flashcard Question 🤔")
    a = st.text_input("Custom Flashcard Answer ✅")
    folder = st.text_input("Folder name (e.g., math_ai)")
    if st.button("💾 Save Custom Flashcard") and q and a and folder:
        os.makedirs(f"flashcards/{folder}", exist_ok=True)
        with open(f"flashcards/{folder}/custom_flashcards.txt", "a", encoding="utf-8") as f:
            f.write(f"Q: {q}\nA: {a}\n\n")
        st.success(f"Flashcard saved to flashcards/{folder}/custom_flashcards.txt 🌸")

    if st.button("🏠 Back to Home"):
        st.session_state.page = "Welcome"
        st.rerun()

# -------------------- Quizzes Page --------------------
if st.session_state.page == "Quizzes":
    st.markdown("<h1 class='quiz-title'>📝 Study Buddy AI Quiz</h1>", unsafe_allow_html=True)

    text = st.text_area("📖 Paste your study text here 🌸")
    if st.button("🎀 Generate Quiz"):
        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role":"user","content":f"Create 5 multiple-choice quiz questions with answers from this:\n\n{text}"}]
        }
        reply = requests.post(url, headers=headers, json=data).json()["choices"][0]["message"]["content"]

        st.subheader("✨ Your Quiz 🤖")
        st.text_area("Generated Quiz", reply, height=300)

        score = random.choice([20, 40, 60, 80, 100])
        st.success(f"🌟 Your Score: {score}/100")

        if score >= 60:
            st.balloons()
            st.audio("https://www.soundjay.com/button/beep-07.wav")
            st.success("🎊 Yay! You did amazing 🤖🌸")
        else:
            st.warning("🌱 Keep going, you’ll get better next time! 🌸")

    if st.button("🏠 Back to Home"):
        st.session_state.page = "Welcome"
        st.rerun()





