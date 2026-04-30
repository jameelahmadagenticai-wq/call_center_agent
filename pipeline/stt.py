from faster_whisper import WhisperModel

# ========================
# LOAD MODEL (once)
# ========================
stt_model = WhisperModel(
    "base",
    device="cpu",         # change to "cuda" if GPU available
    compute_type="int8"
)


# ========================
# TRANSCRIBE FUNCTION
# ========================
def transcribe(audio_file: str) -> str:
    try:
        segments, _ = stt_model.transcribe(
            audio_file,
            language="en"
        )

        text = " ".join([seg.text for seg in segments]).strip()

        if not text:
            print("⚠️ No speech detected")
            return ""

        print(f"🧑 You: {text}")
        return text

    except Exception as e:
        print("❌ STT Error:", e)
        return ""