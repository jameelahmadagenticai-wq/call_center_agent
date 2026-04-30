from pipeline.audio_capture import capture_audio
from pipeline.stt import transcribe
from pipeline.llm import ask_mistral
from pipeline.tts import speak

# ========================
# SYSTEM PROMPT (Agent Personality)
# ========================
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Alex, a professional sales agent for TechCorp. "
        "Be concise and friendly. Limit responses to 2-3 sentences. "
        "Your goal is to schedule a product demo."
    )
}


# ========================
# MAIN LOOP
# ========================
def run_call_loop():
    history = [SYSTEM_PROMPT]

    print("📞 AI Call Agent Started (Press Ctrl+C to stop)\n")

    while True:
        try:
            # Step 1: Capture audio
            audio_file = capture_audio()

            # Step 2: Convert speech to text
            user_text = transcribe(audio_file)

            # Handle weak/empty input
            if not user_text or len(user_text.strip()) < 2:
                print("⚠️ No clear speech detected, try again...")
                continue

            # Exit condition (optional)
            if "bye" in user_text.lower():
                print("👋 Ending call...")
                speak("Thank you for your time. Have a great day!")
                break

            # Step 3: Get AI response
            reply, history = ask_mistral(user_text, history)

            # Step 4: Speak response
            speak(reply)

        except KeyboardInterrupt:
            print("\n🛑 Call ended by user")
            break

        except Exception as e:
            print("❌ Pipeline error:", e)


# ========================
# ENTRY POINT
# ========================
if __name__ == "__main__":
    run_call_loop()