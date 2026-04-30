import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import requests
import subprocess
import winsound
from faster_whisper import WhisperModel

# ========================
# CONFIG
# ========================
SAMPLE_RATE = 16000
DURATION = 5

OLLAMA_URL = "http://localhost:11434/api/chat"

PIPER_PATH = "piper/piper.exe"
MODEL_PATH = "models/en_US-amy-medium.onnx"
OUTPUT_FILE = "reply.wav"

# ========================
# LOAD WHISPER MODEL (once)
# ========================
stt_model = WhisperModel("base", device="cpu", compute_type="int8")


# ========================
# STEP 1 — Record Audio
# ========================
def record_audio():
    print("\n🎤 Speak now...")

    sd.sleep(500)

    audio = sd.rec(
        int(SAMPLE_RATE * DURATION),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16'
    )
    sd.wait()

    # Safe normalization
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))
        audio = (audio * 32767).astype(np.int16)

    wav.write("input.wav", SAMPLE_RATE, audio)

    return "input.wav"


# ========================
# STEP 2 — Whisper (STT)
# ========================
def transcribe(audio_file):
    segments, _ = stt_model.transcribe(audio_file)

    text = " ".join([seg.text for seg in segments]).strip()

    print("🧑 You:", text)
    return text


# ========================
# STEP 3 — Mistral (LLM)
# ========================
def ask_mistral(user_text, history):
    try:
        history.append({"role": "user", "content": user_text})

        payload = {
            "model": "mistral",
            "messages": history,
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload)
        reply = response.json()["message"]["content"]

        history.append({"role": "assistant", "content": reply})

        print("🤖 AI:", reply)
        return reply, history

    except Exception as e:
        print("❌ Mistral error:", e)
        return "Sorry, something went wrong.", history


# ========================
# STEP 4 — Piper (TTS)
# ========================
def speak(text):
    process = subprocess.Popen(
        [PIPER_PATH, "--model", MODEL_PATH, "--output_file", OUTPUT_FILE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    _, err = process.communicate(input=text.encode())

    if err:
        print("⚠️ Piper error:", err.decode())

    # Play audio (Windows)
    winsound.PlaySound(OUTPUT_FILE, winsound.SND_FILENAME)


# ========================
# MAIN LOOP
# ========================
def run():
    history = [{
        "role": "system",
        "content": "You are a helpful AI voice assistant. Keep responses short and clear."
    }]

    print("🚀 AI Voice Agent Started (Press Ctrl+C to stop)\n")

    while True:
        try:
            audio = record_audio()
            text = transcribe(audio)

            # Handle weak/no speech
            if not text or len(text.strip()) < 2:
                print("⚠️ No clear speech detected, try again...")
                continue

            # Exit condition (optional)
            if "bye" in text.lower():
                print("👋 Ending conversation...")
                speak("Goodbye! Have a nice day.")
                break

            reply, history = ask_mistral(text, history)
            speak(reply)

        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
            break

        except Exception as e:
            print("❌ Unexpected error:", e)


# ========================
# ENTRY POINT
# ========================
if __name__ == "__main__":
    run()