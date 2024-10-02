import streamlit as st
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import pandas as pd
import json
from helper import convert_wav_to_text, extract_data, save_in_db
from analysis import analyze_conversation, format_medication

# Constants
SAMPLE_RATE = 44100
CHANNELS = 1
DURATION = 20  # Record for 10 seconds by default

# Initialize session state
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'transcription' not in st.session_state:
    st.session_state.transcription = None
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'final_res' not in st.session_state:
    st.session_state.final_res = None

def start_recording():
    st.session_state.is_recording = True
    st.session_state.audio_data = sd.rec(
        int(SAMPLE_RATE * DURATION),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS
    )

def stop_recording():
    sd.stop()
    st.session_state.is_recording = False

def save_audio():
    if st.session_state.audio_data is not None:
        wav_file = "recording.wav"
        write(wav_file, SAMPLE_RATE, st.session_state.audio_data)
        return wav_file
    return None

def process_audio(wav_file):
    st.session_state.transcription = convert_wav_to_text(wav_file)
    st.session_state.extracted_data = extract_data(st.session_state.transcription)

def main():
    st.title("Medical Consultation Recorder and Analyzer")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Start Recording", disabled=st.session_state.is_recording):
            start_recording()

    with col2:
        if st.button("Stop Recording", disabled=not st.session_state.is_recording):
            stop_recording()
            wav_file = save_audio()
            if wav_file:
                st.success(f"Audio saved as {wav_file}")
                st.audio(wav_file)
                process_audio(wav_file)

    if st.session_state.transcription:
        st.subheader("Transcription")
        st.write(st.session_state.transcription)
        
        res = st.session_state.transcription
        print("check:--------------------------->\n")
        print(res)
        
        result = analyze_conversation(res)

        if result:
            formatted_result = {
                "disease": result.get("disease", ""),
                "medications": [format_medication(med) for med in result.get("medications", [])],
                "next_checkup": result.get("next_checkup", ""),
                "investigations": result.get("additional_tests", [])
            }
            st.subheader("Analysis Result")
            st.session_state.final_res = formatted_result
            print(st.session_state.final_res)
            st.json(formatted_result)
            
            if st.button("Save to Database"):
                save_status = save_in_db(st.session_state.final_res,res)
                if save_status:
                    st.success("Data saved to database successfully!")
                else:
                    st.error("Failed to save data to database. Please try again.")
        else:
            st.write("Failed to analyze conversation.")

if __name__ == "__main__":
    main()