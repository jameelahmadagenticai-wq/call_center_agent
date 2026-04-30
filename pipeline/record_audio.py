import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np

samplerate = 16000
duration = 5

print("Recording... Speak clearly after 1 second")

# small delay so you can prepare
sd.sleep(1000)

audio = sd.rec(
    int(samplerate * duration),
    samplerate=samplerate,
    channels=1,
    dtype='int16'
)

sd.wait()

# normalize audio (important)
audio = audio / np.max(np.abs(audio))

wav.write("test_audio.wav", samplerate, audio)

print("Saved as test_audio.wav")