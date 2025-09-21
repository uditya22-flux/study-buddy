📘 Study Buddy AI

✨ Your personal AI-powered study companion! ✨

Study Buddy AI helps students with:

🧠 Smart Chatbot for Q&A

🎴 Flashcards (auto-generated or custom)

🎮 Fun Quizzes from your study material

🌸 Cute & aesthetic cartoon theme (blue skies & clouds ☁️)

🎉 Rewards with pop-ups & sounds when you do well!

🚀 Features

🤖 AI Chatbot using OpenRouter (GPT-4o-mini)

🎴 Flashcard creation by topic or custom input

📂 Organize flashcards in folders

🎮 Quiz mode with scoring & feedback

🌈 Cartoon-style UI/UX inspired by Study Bunny app

🎶 Sound & animation rewards

🛠️ Tech Stack

Python 3.10+

Streamlit
 for UI

OpenRouter API
 for AI responses

requests, dotenv for API handling



📂 Project Structure
study-buddy/
│── app.py           # Main Streamlit app
│── chatbot.py       # Chatbot logic
│── test_chat.py     # API test script
│── .env             # Secret keys (not shared!)
│── requirements.txt # Dependencies

⚡ Getting Started
1. Clone the repo
git clone https://github.com/uditya22-flux/study_buddyai.git
cd study_buddyai

2. Create virtual environment
python -m venv venv
source venv/Scripts/activate   # On Windows

3. Install dependencies
pip install -r requirements.txt

4. Add your API key

Create a .env file:

OPENROUTER_API_KEY=your_api_key_here

5. Run the app
streamlit run app.py
