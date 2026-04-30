# 📞 AI Cold Call Center Agent

A fully local, AI-powered call center agent capable of handling voice conversations, simulating real cold calls, and automating sales workflows.

---

## 🚀 Overview

This project builds an intelligent voice agent that can:

* 🎤 Listen to user speech (Speech-to-Text)
* 🧠 Understand and respond using LLM (Ollama - Phi3/Mistral)
* 🔊 Speak responses (Text-to-Speech)
* 💬 Maintain conversation context
* 📞 Integrate with telephony systems (Twilio / FreeSWITCH)

All core processing runs **locally** — no external API dependency required.

---

## 🧩 Tech Stack

| Component                | Tool                    |
| ------------------------ | ----------------------- |
| LLM                      | Ollama (Phi3 / Mistral) |
| STT                      | Faster-Whisper          |
| TTS                      | Piper                   |
| UI                       | Streamlit               |
| Backend                  | Python                  |
| Telephony (optional)     | Twilio / FreeSWITCH     |
| Orchestration (optional) | n8n                     |

---

## 🏗️ System Architecture

```
User (Voice / Text)
        ↓
Streamlit UI (Controller)
        ↓
Audio Capture (Mic)
        ↓
Speech-to-Text (Whisper)
        ↓
LLM (Ollama - Phi3)
        ↓
Text Response
        ↓
Text-to-Speech (Piper)
        ↓
Audio Playback
```

---

## 🔁 Conversation Flow

1. User speaks or types input
2. Audio is captured and converted to text
3. Text is sent to the LLM with conversation history
4. LLM generates a contextual response
5. Response is converted to speech
6. Audio is played back to the user

---

## 🧠 Agent Behavior

The agent is configured as a **sales representative (Sarah)** with:

* Goal: Schedule a product demo
* Short, conversational responses (2–3 sentences)
* Objection handling:

  * “too expensive”
  * “not interested”
  * “already have solution”
  * “call back later”

---

## 📁 Project Structure

```
project/
│
├── pipeline/
│   ├── audio_capture.py   # Mic input
│   ├── stt.py             # Speech-to-text
│   ├── llm.py             # LLM + memory + logic
│   ├── tts.py             # Text-to-speech
│
├── streamlit_app.py       # UI controller
├── models/                # TTS models
├── piper/                 # Piper binary
├── input.wav
├── reply.wav
```

---

## ⚙️ Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Install Ollama

```bash
ollama pull phi3
```

---

### 3. Run Streamlit App

```bash
streamlit run streamlit_app.py
```

---

## 📞 Twilio Integration (Optional)

* Used for real phone call interaction
* Requires:

  * Verified number (trial)
  * Or upgraded account
* Twilio communicates via webhooks to your server

---

## ⚡ Performance Optimization

* Use `phi3` for faster responses (CPU-friendly)
* Limit conversation history
* Summarize older messages
* Keep responses short

---

## ⚠️ Limitations

* Twilio trial restricts unverified numbers
* Latency depends on local hardware
* Piper voice may sound robotic (can be improved with better models)

---

## 🔮 Future Improvements

* Real-time streaming conversation
* Interrupt handling (barge-in)
* Advanced agent state (intro → pitch → close)
* CRM integration
* Multi-agent orchestration

---

## 👨‍💻 Author

Developed as a local AI call center solution using modern LLM and voice technologies.

---

## 📌 Summary

This project demonstrates how to build a **fully local AI voice agent** capable of simulating real-world cold calls with minimal cost and high flexibility.
