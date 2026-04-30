import requests

# ========================
# CONFIG
# ========================
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "phi3"
MAX_HISTORY = 10


# ========================
# SYSTEM PROMPT
# ========================
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
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
}


# ========================
# OBJECTIONS
# ========================
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


# ========================
# DETECT OBJECTION
# ========================
def detect_objection(text):
    txt = text.lower()
    for key in OBJECTIONS:
        if key in txt:
            return OBJECTIONS[key]
    return None


# ========================
# SUMMARIZE HISTORY
# ========================
def summarize_history(history):
    try:
        payload = {
            "model": MODEL_NAME,
            "messages": history + [{
                "role": "user",
                "content": "Summarize this conversation in 3 short bullet points."
            }],
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        return response.json()["message"]["content"]

    except Exception as e:
        print("❌ Summary Error:", e)
        return None


# ========================
# MEMORY MANAGER
# ========================
def manage_memory(history):
    if len(history) <= MAX_HISTORY:
        return history

    old_part = history[:-6]
    recent_part = history[-6:]

    summary = summarize_history(old_part)

    if summary:
        return [
            SYSTEM_PROMPT,
            {
                "role": "system",
                "content": f"Conversation summary: {summary}"
            }
        ] + recent_part

    return history


# ========================
# MAIN FUNCTION
# ========================
def ask_mistral(user_text, history):
    try:
        # Add user input
        history.append({
            "role": "user",
            "content": user_text
        })

        # 🔥 Objection handling
        objection = detect_objection(user_text)
        if objection:
            context = f"User said: '{user_text}'. Suggested response: {objection}"
            history.append({"role": "system", "content": context})

        # 🔥 Memory control
        history = manage_memory(history)

        payload = {
            "model": MODEL_NAME,
            "messages": history,
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        reply = response.json()["message"]["content"]

        history.append({
            "role": "assistant",
            "content": reply
        })

        return reply, history

    except Exception as e:
        print("❌ LLM Error:", e)
        return "Sorry, I had a delay. Could you repeat that briefly?", history