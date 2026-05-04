from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

import shutil
import os
import uuid

from voice_pipeline import transcribe, ask_mistral, speak

app = FastAPI()

# ========================
# 🧠 SESSION MEMORY
# ========================
sessions = {}

SYSTEM_PROMPT = {
    "role": "system",
    "content": "You are a sales call agent. Keep responses short and persuasive."
}


def get_history(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = [SYSTEM_PROMPT.copy()]
    return sessions[session_id]


def update_history(session_id: str, history):
    sessions[session_id] = history


# ========================
# 🔁 SHARED LOGIC
# ========================
def process_message(user_text: str, session_id: str):
    history = get_history(session_id)

    try:
        reply, history = ask_mistral(user_text, history)
        update_history(session_id, history)
        return reply
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# 🎤 VOICE ENDPOINT
# ========================
@app.post("/voice")
async def voice_agent(
    file: UploadFile = File(...),
    session_id: str = "default"
):
    # unique temp file
    temp_input = f"temp_{uuid.uuid4()}.ogg"

    with open(temp_input, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 🎤 STT
        text = transcribe(temp_input)

        if not text or len(text.strip()) < 2:
            raise HTTPException(status_code=400, detail="No speech detected")

        # 🤖 LLM
        reply = process_message(text, session_id)

        # 🔊 TTS
        audio_path = speak(reply)

        # 📤 RETURN AUDIO
        return FileResponse(
            path=audio_path,
            media_type="audio/ogg",
            filename="reply.ogg",
            background=BackgroundTask(lambda: os.remove(audio_path))
        )

    finally:
        # cleanup input
        if os.path.exists(temp_input):
            os.remove(temp_input)


# ========================
# 💬 CHAT ENDPOINT
# ========================
class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat_agent(
    req: ChatRequest,
    session_id: str = "default"
):
    user_text = req.message

    if not user_text or len(user_text.strip()) < 1:
        raise HTTPException(status_code=400, detail="Empty message")

    reply = process_message(user_text, session_id)

    return {
        "user": user_text,
        "reply": reply
    }