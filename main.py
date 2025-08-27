import streamlit as st
from audiorecorder import audiorecorder
from utils import process_audio, azure_stt, google_stt
import time

LANGUAGES = ["en-GB", "nl-BE", "nl-NL", "de-DE", "fr-FR"]
KEYS = {
    "AZURE_KEY": st.secrets["AZURE_KEY"],
    "GOOGLE_KEY": st.secrets["GOOGLE_KEY"]
}


def run_stt(header, function, audio, language, key):
    with st.spinner(f"Transcribing {header}..."):
        st.subheader(header)
        start_time = time.time()
        result = function(audio, language, key)
        delta = time.time() - start_time
        st.info(f"Elapsed time: {delta:.2f}s")
    if "Error" not in result:
        with st.container():
            st.info(result)
    else:
        st.error(f"❌ Transcription Failed: {result}")


def run_app():
    st.set_page_config(page_title="STT test", page_icon="🎙️")
    st.title("STT test")
    language = st.sidebar.selectbox("Select language:", LANGUAGES)

    audio = audiorecorder("🎙️ Start recording", "🔴 Stop recording", key="audio")

    if len(audio) > 0:
        st.audio(audio.export().read(), format="audio/wav")
        audio_bytes, audio_path = process_audio(audio)
        run_stt("Azure STT", azure_stt, audio_path, language, KEYS["AZURE_KEY"])
        run_stt("Google STT", google_stt, audio_bytes, language, KEYS["GOOGLE_KEY"])


if __name__ == "__main__":
    run_app()
