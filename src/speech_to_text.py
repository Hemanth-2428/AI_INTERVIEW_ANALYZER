import tempfile
import time

import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import streamlit as st
import whisper


model = whisper.load_model("small")
SAMPLERATE = 16000


class AudioRecorder:
    def __init__(self, samplerate=SAMPLERATE):
        self.samplerate = samplerate
        self.audio_buffer = []
        self.stream = None
        self.start_time = None

    def start(self):
        self.audio_buffer = []
        self.start_time = time.time()

        def callback(indata, frames, time_info, status):
            if status:
                print(status)
            self.audio_buffer.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            dtype="float32",
            callback=callback,
        )
        self.stream.start()

    def stop(self):
        if self.stream is None:
            return "", 0

        try:
            self.stream.stop()
            self.stream.close()
        except Exception:
            pass

        self.stream = None

        if not self.audio_buffer:
            return "", 0

        audio = np.concatenate(self.audio_buffer, axis=0).flatten().astype(np.float32)
        duration = len(audio) / self.samplerate

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            wav.write(tmpfile.name, self.samplerate, audio)
            result = model.transcribe(
                tmpfile.name,
                language="en",
                fp16=False,
                temperature=0.0,
                beam_size=5,
            )

        return result["text"].strip(), duration


def get_recorder():
    if "audio_recorder" not in st.session_state:
        st.session_state.audio_recorder = AudioRecorder()
    return st.session_state.audio_recorder


def start_recording():
    recorder = get_recorder()
    recorder.start()
    st.session_state.recording = True


def stop_recording():
    recorder = get_recorder()
    text, duration = recorder.stop()
    st.session_state.recording = False
    return text, duration
