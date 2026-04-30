from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
import requests

app = FastAPI()

# =========================
# 🔥 SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
You are Sarah, a confident and friendly sales representative at TechSolutions Pvt Ltd.

You are speaking on a live phone call with a potential business client.

Your primary goal:
Schedule a 15-minute product demo.

Rules:
- Keep responses under 2 sentences
- Be natural and conversational
- Ask one question at a time
- If user says "not interested" twice, end politely
"""

# =========================
# 🔥 OBJECTIONS
# =========================
OBJECTIONS = {
    'too expensive': (
        'I completely understand budget is a concern. '
        'Most clients see ROI within 60 days — would it help '
        'if I showed you a quick cost-benefit breakdown?'
    ),
    'not interested': (
        'That is totally fair. Could I ask — what would need to '
        'change for this to be relevant to your business?'
    ),
    'already have solution': (
        'Great that you have something in place. Many of our clients '
        'switched after comparing. Would a quick comparison be useful?'
    ),
    'call back later': (
        'Of course! When would be a good time? I can schedule a '
        'specific slot so I do not interrupt you again.'
    ),
}

def detect_objection(text):
    for key in OBJECTIONS:
        if key in text.lower():
            return OBJECTIONS[key]
    return None


# =========================
# 🔥 MEMORY MANAGER
# =========================
MAX_HISTORY = 20

def manage_memory(history, user_msg, ai_msg):
    history.append({'role': 'user', 'content': user_msg})
    history.append({'role': 'assistant', 'content': ai_msg})

    if len(history) > MAX_HISTORY + 1:
        system = history[0]
        history = [system] + history[-MAX_HISTORY:]

    return history


def summarize_call(history):
    payload = {
        "model": "mistral",
        "messages": history + [{
            "role": "user",
            "content": "Summarize this call in 3 bullet points: outcome, interest level, next step."
        }],
        "stream": False
    }
    res = requests.post(OLLAMA_URL, json=payload)
    return res.json()["message"]["content"]


# =========================
# 🔥 STATE MACHINE
# =========================
class CallState:
    INTRO = 'intro'
    DISCOVERY = 'discovery'
    PITCH = 'pitch'
    OBJECTION = 'objection'
    CLOSING = 'closing'
    ENDED = 'ended'


# =========================
# 🔥 SESSION
# =========================
class AgentSession:
    def __init__(self):
        self.state = CallState.INTRO
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.no_count = 0

    def update_state(self, user_text):
        txt = user_text.lower()

        if 'not interested' in txt or 'no thanks' in txt:
            self.no_count += 1
            self.state = CallState.ENDED if self.no_count >= 2 else CallState.OBJECTION

        elif 'yes' in txt or 'interested' in txt:
            self.state = CallState.CLOSING

        elif self.state == CallState.INTRO:
            self.state = CallState.DISCOVERY

        elif self.state == CallState.DISCOVERY:
            self.state = CallState.PITCH


# =========================
# 🔥 STORAGE
# =========================
sessions = {}

OLLAMA_URL = "http://localhost:11434/api/chat"
BASE_URL = "https://unlethal-preelective-dalila.ngrok-free.dev"


# =========================
# 🔥 LLM CALL
# =========================
def ask_mistral(session, user_text):
    payload = {
        "model": "mistral",
        "messages": session.history + [{"role": "user", "content": user_text}],
        "stream": False
    }

    res = requests.post(OLLAMA_URL, json=payload)
    reply = res.json()["message"]["content"]

    session.history = manage_memory(session.history, user_text, reply)

    return reply


# =========================
# 🔥 SMART REPLY (STEP 5)
# =========================
def generate_reply(session, user_text):

    session.update_state(user_text)

    if session.state == CallState.ENDED:
        return "Thank you for your time. Have a wonderful day!"

    objection = detect_objection(user_text)

    if objection:
        context = (
            f'The prospect said: "{user_text}". '
            f'Suggested response: {objection}. '
            f'Adapt it naturally.'
        )
        return ask_mistral(session, context)

    return ask_mistral(session, user_text)


# =========================
# 🔥 TWILIO ENDPOINT
# =========================
@app.post("/voice")
async def voice(request: Request):
    form = await request.form()

    call_sid = form.get("CallSid")
    user_input = form.get("SpeechResult", "")

    if call_sid not in sessions:
        sessions[call_sid] = AgentSession()

    session = sessions[call_sid]

    response = VoiceResponse()

    # FIRST TURN
    if not user_input:
        gather = response.gather(
            input="speech",
            action=f"{BASE_URL}/voice",
            method="POST",
            speechTimeout="auto"
        )
        gather.say("Hello, this is Sarah from TechSolutions. May I know your name?")
        return Response(str(response), media_type="application/xml")

    # 🔥 MAIN LOGIC
    reply = generate_reply(session, user_input)

    # 🔴 END CALL
    if session.state == CallState.ENDED:
        summary = summarize_call(session.history)
        print("\n📊 CALL SUMMARY:\n", summary)

        response.say(reply)
        return Response(str(response), media_type="application/xml")

    # 🔁 CONTINUE LOOP
    gather = response.gather(
        input="speech",
        action=f"{BASE_URL}/voice",
        method="POST",
        speechTimeout="auto"
    )
    gather.say(reply)

    return Response(str(response), media_type="application/xml")

# 🔥 SIMPLE CHAT ENDPOINT (for Streamlit)
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()

    session_id = data.get("session_id", "web_user")
    user_text = data.get("message", "")

    if session_id not in sessions:
        sessions[session_id] = AgentSession()

    session = sessions[session_id]

    reply = generate_reply(session, user_text)

    return {
        "reply": reply,
        "state": session.state
    }