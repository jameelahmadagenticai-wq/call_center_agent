import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np

SAMPLE_RATE = 16000
DURATION = 10  # seconds


def capture_audio(filename="input.wav"):
    print("\n🎤 Listening...")

    # small delay so user can prepare
    sd.sleep(500)

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    # Safe normalization
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))
        audio = (audio * 32767).astype(np.int16)

    wav.write(filename, SAMPLE_RATE, audio)

    print(f"✅ Audio saved: {filename}")
    return filename