import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from groq import Groq

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lingualab-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
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
    f"You are a precise translator. Translate this chat message into {DIALECTS[dialect]}.\n\n"
    f"STRICT RULES:\n"
    f"- Preserve the EXACT meaning, do not change what the person is saying\n"
    f"- Only change the vocabulary and style to match the domain\n"
    f"- ONE line only, short like a chat message\n"
    f"- No hallucinations, no random words, no philosophy\n"
    f"- If someone says 'I am tired', say it in domain language meaning 'I am tired'\n"
    f"- If someone says 'where are you', say it in domain language meaning 'where are you'\n\n"
    f"EXAMPLES for Python dialect:\n"
    f"'I am tired' → 'energy.drain() # battery low'\n"
    f"'where are you' → 'user.get_location()'\n"
    f"'I am hungry' → 'stomach.isEmpty() == True'\n"
    f"'how are you' → 'status.check(user)'\n\n"
    f"EXAMPLES for Finance dialect:\n"
    f"'I am tired' → 'Current energy reserves at critical low, immediate rest allocation required'\n"
    f"'where are you' → 'Please disclose your current geographical position'\n"
    f"'I am hungry' → 'Caloric deficit detected, immediate nutritional investment required'\n\n"
    f"EXAMPLES for Medical dialect:\n"
    f"'I am tired' → 'Patient presents with acute fatigue and decreased energy levels'\n"
    f"'I am hungry' → 'Patient experiencing hypoglycemic symptoms, oral intake recommended'\n\n"
    f"Now translate this message: {message}\n"
    f"Dialect: {DIALECTS[dialect]}\n"
    f"Translation (one line only):"
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
