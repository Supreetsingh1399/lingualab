# 🌐 LinguaLab

> Chat in any language of thought — Python, Finance, Medical, Legal, Math, Gen Z

LinguaLab is a real-time multi-user chat app where every message gets translated into a domain-specific language. Only experts in that domain can read and understand the messages — like a secret language between professionals.

## 💡 The Idea

Imagine a programmer and a doctor chatting. The programmer sees every message as Python code. The doctor sees the same message as clinical terminology. Neither can read the other's version without domain knowledge.

## ✨ Features

- 💬 Real-time chat using WebSockets (Socket.io)
- 🐍 Python, ⚡ JavaScript, 💰 Finance, 🏥 Medical, ⚖️ Legal, 📐 Math, 😎 Gen Z dialects
- 👁 "Show original" to reveal the plain English message
- 💡 "Explain this" to get a plain English explanation
- 🏠 Create or join rooms with a room code
- 🤖 Powered by LLaMA 3.3 70B via Groq API (free)
- 📱 Built entirely on Android using Termux

## 🚀 Live Demo

👉 [lingualab.up.railway.app](https://lingualab.up.railway.app) ← update this after deploying

## 🛠 Tech Stack

- Python + Flask
- Flask-SocketIO (real-time messaging)
- Groq API (LLaMA 3.3 70B) — free tier
- Vanilla HTML/CSS/JS
- Deployed on Railway

## ⚙️ Run Locally

1. Clone the repo
   git clone https://github.com/yourusername/lingualab
   cd lingualab

2. Install dependencies
   pip install -r requirements.txt

3. Get a free API key from https://console.groq.com

4. Set your key
   export GROQ_API_KEY="your-key-here"

5. Run
   python app.py

6. Open http://localhost:5000

## 🧠 How It Works

1. User types a message in plain English
2. Server sends it to LLaMA 3.3 70B via Groq
3. AI translates it into the user's chosen dialect
4. Translated message is broadcast to the room via WebSocket
5. Each user sees the message in THEIR chosen dialect
6. Hit "show original" or "explain this" to decode any message

## 📱 Built on Mobile

This entire project was built on an Android phone using Termux — no laptop, no PC.

## 📄 License

MIT
