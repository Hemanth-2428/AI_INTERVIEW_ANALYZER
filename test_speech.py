from src.speech_to_text import record_audio

print("Testing microphone...")

text = record_audio()

print("Final output:", text)
