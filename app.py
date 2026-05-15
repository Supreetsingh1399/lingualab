import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from groq import Groq

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lingualab-secret'
socketio = SocketIO(app, cors_allowed_origins="*")
client = Groq(api_key=os.environ.get("GROQ_API_KEY")) 

DIALECTS = {
    "english": "plain simple English",
    "python": "real Python code only — use variables, functions, lists, dicts, classes naturally as if the message IS code. No print statements. No comments. Only someone who codes in Python daily would understand it.",
    "javascript": "real JavaScript only — use callbacks, promises, array methods, objects naturally as if the message IS JS code. No comments. Only a JS developer would understand it.",
    "finance": "deep finance/commerce jargon — use terms like EBITDA, liquidity, market cap, ROI, hedge, portfolio, fiscal, equity, amortize naturally in a sentence. Only a finance professional would understand it.",
    "medical": "real clinical medical language — use anatomical terms, Latin medical terms, diagnoses, symptoms, procedures naturally. Only a doctor or medical student would understand it.",
    "legal": "dense legal language — use terms like whereas, hereinafter, pursuant to, indemnify, tort, plaintiff, affidavit, jurisdiction naturally. Only a lawyer would understand it.",
    "math": "pure mathematical language — use set notation, functions, proofs, variables, equations naturally to express the message. Only a mathematician would understand it.",
    "gen-z": "pure Gen Z internet slang — use terms like no cap, bussin, slay, rizz, lowkey, NPC, understood the assignment, it's giving, main character naturally. Only Gen Z would fully get it.",
}

MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]

def translate(message, dialect):
    if dialect == "english":
        return message
    prompt = (
    f"You are translating a chat message into a secret domain language.\n"
    f"Rules:\n"
    f"- Translate into: {DIALECTS[dialect]}\n"
    f"- ONE line only — like a real chat message, not an essay\n"
    f"- So authentic that ONLY an expert in that domain would understand\n"
    f"- Someone outside the domain should find it confusing or unreadable\n"
    f"- No explanations, no labels, no 'Translation:' prefix\n"
    f"- Reply with ONLY the translated message\n\n"
    f"Original message: {message}"
)
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                continue
            return f"[Error: {str(e)}]"
    return "[All models rate limited, try again in a moment]"

def explain(message):
    prompt = (
        f"Explain this message in very simple plain English "
        f"in one or two sentences max.\n\n"
        f"Message: {message}"
    )
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                continue
            return f"[Error: {str(e)}]"
    return "[All models rate limited]"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat/<room>')
def chat(room):
    return render_template('chat.html', room=room)

@socketio.on('join')
def on_join(data):
    room = data['room']
    username = data['username']
    join_room(room)
    emit('system', {'msg': f"{username} joined"}, to=room)

@socketio.on('message')
def on_message(data):
    room = data['room']
    username = data['username']
    original = data['message']
    dialect = data.get('dialect', 'english')
    print(f"MSG RECEIVED: {username} in {room}: {original}")
    translated = translate(original, dialect)
    print(f"TRANSLATED: {translated}")
    emit('message', {
        'username': username,
        'original': original,
        'translated': translated,
        'dialect': dialect,
    }, to=room)
    print(f"EMITTED to room: {room}")

@socketio.on('explain')
def on_explain(data):
    explanation = explain(data['message'])
    emit('explanation', {
        'original': data['message'],
        'explanation': explanation
    })

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    username = data['username']
    leave_room(room)
    emit('system', {'msg': f"{username} left"}, to=room)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"\n LinguaLab running at http://localhost:{port}\n")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
