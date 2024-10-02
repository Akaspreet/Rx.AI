import streamlit as st
from modules.audio_processing import speech_to_text, text_to_speech
from modules.translation import translate_text, summarize_text
from modules.gemini_api import generate_text
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import io
import google.generativeai as genai
import json
import re

# Configure the Gemini API
genai.configure(api_key='AIzaSyCvHfiUg5GEdqj7BhuZ6VOqcIzgxbbRGu4')

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

# Function to analyze conversation
def analyze_conversation(conversation):
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Analyze the following doctor-patient conversation and extract key medical information.
    Return the results in JSON format with the following structure:
    {{
        "disease": "Identified disease or condition",
        "medications": [
            {{
                "name": "Medication name",
                "type": "Medication type (e.g., Tab)",
                "dosage": "Dosage amount",
                "count": "Number of doses per time",
                "frequency": "How often to take (e.g., twice a day)",
                "duration": "Duration of treatment",
                "meal_relation": "Relation to meal (e.g., before meal, after meal)"
            }}
        ],
        "precautions": ["List of precautions"],
        "next_checkup": "Date or timeframe for next appointment",
        "additional_tests": ["List of any additional tests required"],
        "investigations": ["Any other advice or recommendations"]
    }}
    Conversation:
    {conversation}
    """
    
    response = model.generate_content(prompt)
    
    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group())
            return result
        except json.JSONDecodeError:
            st.error("Error: Unable to parse JSON response")
            return None
    else:
        st.error("Error: No JSON found in the response")
        return None

def format_medication(med):
    return {
        "medicine name": med['name'],
        "medtype": med['type'],
        "dosage": med['dosage'],
        "med_count": med['count'],
        "Timing": med['frequency'],
        "duration": med['duration'],
        "meal_timing": med['meal_relation'] if 'before' in med['meal_relation'].lower() else "after meal"
    }

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
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

def main():
    st.title("Audio Translation, Summarization & Analysis App")
    st.markdown("This app allows you to upload or record audio, convert it to text, translate it, summarize it, and analyze the conversation for medical information.")

    # Dropdown for audio input method
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
            temp_file = save_wav_to_bytesio(audio_data, sample_rate)
            st.session_state.audio_file = temp_file

    # Convert speech to text
    if st.session_state.audio_file is not None:
        if st.button("Transcribe Audio"):
            st.session_state.transcription = speech_to_text(st.session_state.audio_file)
            st.subheader("Transcription")
            st.write(st.session_state.transcription)

        # Show transcription if it already exists
        if st.session_state.transcription:
            st.subheader("Transcription")
            st.write(st.session_state.transcription)

        # Analyze the conversation
        if st.session_state.transcription and st.button("Analyze Conversation"):
            result = analyze_conversation(st.session_state.transcription)
            if result:
                formatted_result = {
                    "disease": result.get("disease", ""),
                    "medications": [format_medication(med) for med in result.get("medications", [])],
                    "precautions": result.get("precautions", []),
                    "next_checkup": result.get("next_checkup", ""),
                    "additional_tests": result.get("additional_tests", []),
                    "investigations": result.get("investigations", [])
                }
                st.session_state.analysis_result = formatted_result
                st.subheader("Conversation Analysis")
                st.json(formatted_result)
            else:
                st.error("Failed to analyze conversation.")

        # Show analysis result if it already exists
        if st.session_state.analysis_result:
            st.subheader("Conversation Analysis")
            st.json(st.session_state.analysis_result)

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