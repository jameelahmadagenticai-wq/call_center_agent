import streamlit as st
import time
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Cold Call Agent", layout="centered")

# ---- IMPORT PIPELINE ----
from pipeline.audio_capture import capture_audio
from pipeline.stt import transcribe
from pipeline.llm import ask_mistral, SYSTEM_PROMPT
from pipeline.tts import speak

# ---------------- SESSION STATE ----------------
if "history" not in st.session_state:
    st.session_state.history = [SYSTEM_PROMPT]  # ✅ ONLY ONE INIT

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- UI ----------------
st.title("📞 AI Cold Call Agent")
st.caption("Voice + Text Powered Sales Agent")

col1, col2 = st.columns(2)

with col1:
    voice_btn = st.button("🎤 Speak")

with col2:
    enable_voice = st.checkbox("🔊 Voice Reply", value=True)

# ---- TEXT INPUT ----
user_text_input = st.text_input("💬 Type your message")

# ---------------- INPUT HANDLING ----------------
user_text = None

if voice_btn:
    with st.spinner("🎤 Listening..."):
        audio_file = capture_audio()

    with st.spinner("🧠 Transcribing..."):
        user_text = transcribe(audio_file)

elif user_text_input:
    user_text = user_text_input

# ---------------- PROCESS ----------------
if user_text:

    # Show user message
    st.session_state.messages.append(("user", user_text))
    st.chat_message("user").write(user_text)

    # AI response
    with st.spinner("🤖 Thinking..."):
        reply, st.session_state.history = ask_mistral(
            user_text,
            st.session_state.history
        )

    # Show AI message
    st.session_state.messages.append(("assistant", reply))
    st.chat_message("assistant").write(reply)

    # ---------------- AUDIO ----------------
    if enable_voice:
        with st.spinner("🔊 Speaking..."):
            audio_path = speak(reply)

        if audio_path and os.path.exists(audio_path):
            time.sleep(0.3)

            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            st.audio(audio_bytes, format="audio/wav", autoplay=True)
        else:
            st.error("❌ Audio not generated")

# ---------------- HISTORY ----------------
st.divider()
st.subheader("🧾 Conversation History")

for role, msg in st.session_state.messages:
    if role == "user":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Agent:** {msg}")