import subprocess
import os

# ========================
# CONFIG
# ========================
PIPER_PATH = "piper/piper.exe"
MODEL_PATH = "models/en_US-amy-medium.onnx"


# ========================
# TTS FUNCTION
# ========================
def speak(text: str, output_file: str = "reply.wav"):
    try:
        # Run Piper
        process = subprocess.Popen(
            [PIPER_PATH, "--model", MODEL_PATH, "--output_file", output_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        _, err = process.communicate(input=text.encode())

        # Log Piper errors (if any)
        if err:
            print("⚠️ Piper error:", err.decode())

        # ========================
        # VALIDATE OUTPUT FILE
        # ========================
        if not os.path.exists(output_file):
            print("❌ Audio file not created")
            return None

        if os.path.getsize(output_file) == 0:
            print("❌ Audio file is empty")
            return None

        return output_file

    except Exception as e:
        print("❌ TTS Error:", e)
        return None