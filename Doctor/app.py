import streamlit as st
from modules.audio_processing import speech_to_text, text_to_speech
from modules.translation import translate_text, summarize_text
from modules.gemini_api import generate_text
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import io

# Language options
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Russian": "ru",
    "Chinese (Simplified)": "zh-cn",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Turkish": "tr",
    "Swedish": "sv",
    "Danish": "da",
    "Hindi": "hi"
}

# Function to record audio
def record(duration, sample_rate):
    st.write("Recording...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2)
    sd.wait()  # Wait until the recording is finished
    return audio_data

# Function to save audio to a BytesIO object
def save_wav_to_bytesio(audio_data, sample_rate):
    temp_file = io.BytesIO()
    wav.write(temp_file, sample_rate, (audio_data * 32767).astype(np.int16))  # Convert float32 to int16
    temp_file.seek(0)  # Rewind the BytesIO object
    return temp_file

# Initialize session state for variables
if 'transcription' not in st.session_state:
    st.session_state.transcription = None
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'sample_rate' not in st.session_state:
    st.session_state.sample_rate = None

def main():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Arial:wght@400;700&display=swap');
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f7f7f7;
            color: #333;
        }
        h1 {
            color: #0056b3;
        }
        h2 {
            color: #007bff;
        }
        .stButton>button {
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        .stSelectbox>div {
            background-color: #ffffff;
            border-radius: 5px;
            border: 1px solid #cccccc;
            padding: 5px;
        }
        .stFileUploader>div {
            border: 2px dashed #007bff;
            padding: 10px;
            border-radius: 5px;
        }
        .stText {
            font-size: 16px;
            line-height: 1.5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    

    st.title("Audio Translation & Summarization App")
    st.markdown("This app allows you to upload or record audio, convert it to text, translate it into a selected language, generate audio from the translated text, and summarize the original transcription.")

    # Dropdown for audio input method
    st.header("Choose Audio Input Method")
    input_method = st.selectbox("Select Audio Input Method", ["Upload Audio", "Record Audio"])

    if input_method == "Upload Audio":
        uploaded_file = st.file_uploader("Choose an audio file...", type=["wav", "mp3", "m4a"])
        if uploaded_file is not None:
            st.session_state.audio_file = uploaded_file
            st.audio(uploaded_file)

    elif input_method == "Record Audio":
        duration = st.slider("Select recording duration (seconds)", 1, 60, 10)
        sample_rate = 44100  # Common sample rate
        if st.button("Start Recording"):
            audio_data = record(duration, sample_rate)
            # Save to a BytesIO object
            temp_file = save_wav_to_bytesio(audio_data, sample_rate)
            st.session_state.audio_file = temp_file

    # Convert speech to text
    if st.session_state.audio_file is not None:
        if st.button("Transcribe Audio"):
            st.session_state.transcription = speech_to_text(st.session_state.audio_file)
            st.subheader("Transcription")
            st.write(st.session_state.transcription)
            output_hai = st.session_state.transcription
            print(output_hai)

        # Show transcription if it already exists
        if st.session_state.transcription:
            st.subheader("Transcription")
            st.write(st.session_state.transcription)

        # Translate the text (if transcription is available)
        if st.session_state.transcription:


            target_lang = st.selectbox("Choose the target language", list(LANGUAGES.keys()))

            if st.button("Translate Text"):
                st.session_state.translated_text = translate_text(st.session_state.transcription, LANGUAGES[target_lang])
                st.subheader("Translated Text")
                st.write(st.session_state.translated_text)

            # Show translated text if it already exists
            if st.session_state.translated_text:
                st.subheader("Translated Text")
                st.write(st.session_state.translated_text)

            # Text-to-Speech of Translated Text
            if st.session_state.translated_text and st.button("Play Translated Audio"):
                translated_audio = text_to_speech(st.session_state.translated_text, lang=LANGUAGES[target_lang])
                st.subheader("Translated Audio")
                st.audio(translated_audio, format="audio/wav")

        # Summarize the Text (if transcription is available)
        if st.session_state.transcription and st.button("Summarize Text"):
            st.session_state.summary = summarize_text(st.session_state.transcription)
            st.subheader("Summary of Transcription")
            st.write(st.session_state.summary)



if __name__ == "__main__":
    main()
