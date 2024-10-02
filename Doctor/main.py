import streamlit as st
import pandas as pd
from prep_organiser import get_prescriptions_by_disease, get_prescriptions_by_doctor
from summarizer import get_patient_details
import mysql.connector
import pandas as pd
import google.generativeai as genai
from datetime import date
from datetime import datetime, timedelta
from twilio.rest import Client
from email import encoders
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from alerts import trigger_alert
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


# get_patient_details(pat_id)
# Load CSV data into DataFrames
doctor_df = pd.read_csv('/home/usl-sz-1487/Downloads/Hackathon/Doctor/doctors.csv')
patients_df = pd.read_csv('/home/usl-sz-1487/Downloads/Hackathon/Doctor/patients.csv')
patient_history_df = pd.read_csv('/home/usl-sz-1487/Downloads/Hackathon/Doctor/patient_history_.csv')
prescription_df = pd.read_csv('/home/usl-sz-1487/Downloads/Hackathon/Doctor/prescription.csv')

# Define the menu items
menu_items = [
    {"label": "Patient Listing", "icon": "📋", "path": "/patient_listing"},
    {"label": "Patient Details", "icon": "➕", "path": "/patient_details"},
    {"label": "AI Patient Profile", "icon": "🤖", "path": "/ai_patient_profile"},
    {"label": "AI Alerts", "icon": "🤖", "path": "/ai_alerts"},
    {"label": "Voice Prescription Generation", "icon": "🤖", "path": "/voice_prescription"},
]

# Sidebar content
def sidebar_content():
    st.sidebar.image("https://www.unthinkable.co/wp-content/uploads/2022/08/cropped-footer-logo.webp", width=150)
    st.sidebar.title("Doctor Portal")
    
    # Menu items
    for item in menu_items:
        if st.sidebar.button(f"{item['icon']} {item['label']}", key=item['label']):
            st.session_state.page = item['path']

    # Footer
    st.sidebar.markdown("© 2024 Unthinkable Apes")

# Patient Listing Page
def patient_listing_page():
    st.title("Patient Listing")
    st.write("Select a patient from the list below:")
    
    patient_names = patients_df[['first_name', 'last_name']].apply(lambda x: ' '.join(x), axis=1)
    selected_patient_name = st.selectbox('Choose a patient:', patient_names)
    
    if selected_patient_name:
        patient_id = patients_df[patients_df.apply(lambda row: ' '.join([row['first_name'], row['last_name']]) == selected_patient_name, axis=1)]['patient_id'].values[0]
        
        # Display prescriptions for selected patient
        st.write("Prescriptions:")
        patient_prescriptions = prescription_df[prescription_df['patient_id'] == patient_id]
        st.write(patient_prescriptions)
 
# Patient Details Page with Prescription Organizer
def patient_details_page():
    st.title("Patient Details")
    st.write("Select a patient from the list below:")
    
    patient_names = patients_df[['first_name', 'last_name']].apply(lambda x: ' '.join(x), axis=1)
    selected_patient_name = st.selectbox('Choose a patient:', patient_names)
    
    if selected_patient_name:
        patient_id = patients_df[patients_df.apply(lambda row: ' '.join([row['first_name'], row['last_name']]) == selected_patient_name, axis=1)]['patient_id'].values[0]
        
        # Basic patient details in a table
        st.subheader("Patient Basic Details")
        patient_details = patients_df[patients_df['patient_id'] == patient_id].iloc[0]
        basic_details = {
            'Name': f"{patient_details['first_name']} {patient_details['last_name']}",
            'Gender': patient_details['gender'],
            'Phone Number': patient_details['phone_number'],
            'Email': patient_details['email'],
            'City': patient_details['city'],
            'Country': patient_details['country'],
            'Height (cm)': patient_details['height'],
            'Weight (kg)': patient_details['weight'],
            'Blood Type': patient_details['blood_type'],
            'Allergies': patient_details['allergies'],
            'Age': patient_details['age']
        }
        st.table(pd.DataFrame(basic_details.items(), columns=["Detail", "Value"]))

        # Patient history in a table
        st.subheader("Patient Profiler")
        patient_history = patient_history_df[patient_history_df['pat_id'] == patient_id]
        if not patient_history.empty:
            patient_history_table = patient_history[['investigation', 'symptoms', 'summary', 'created_at']]
            patient_history_table.columns = ['Investigation', 'Symptoms', 'Summary', 'Date']
            st.table(patient_history_table)
        else:
            st.write("No history available.")

        # Prescriptions with doctor name and disease (summary) in a separate table
        st.subheader("Prescriptions")
        # Merge prescription_df with doctor_df and patient_history_df to replace doc_id with doctor name and include disease (summary)
       
        patient_prescriptions = prescription_df[prescription_df['patient_id'] == patient_id] \
            .merge(doctor_df, left_on='doc_id', right_on='id', how='left') \
            .merge(patient_history_df[['id', 'summary']], left_on='patient_history', right_on='id', how='left')
        # Drop duplicates to avoid repeated rows
        patient_prescriptions = patient_prescriptions.drop_duplicates()

        if not patient_prescriptions.empty:
            # Select relevant columns and rename
            patient_prescription_table = patient_prescriptions[['medicine', 'duration', 'dosage', 'timing', 'name', 'summary', 'created_at']]
            patient_prescription_table.columns = ['Medicine', 'Duration', 'Dosage', 'Timing', 'Doctor Name', 'Disease (Summary)', 'Date']
            st.table(patient_prescription_table)
        else:
            st.write("No prescriptions available.")
        # Prescription Organizer (Filter buttons)
        st.subheader("Prescription Organizer")
        
        filter_choice = st.radio("Filter prescriptions by:", ["Doctor", "Disease"])
        if selected_patient_name:
            patient_id = patients_df[patients_df.apply(lambda row: ' '.join([row['first_name'], row['last_name']]) == selected_patient_name, axis=1)]['patient_id'].values[0]

            # Find the unique doctor_ids from the prescription data for the selected patient
            doctor_ids = prescription_df[prescription_df['patient_id'] == patient_id]['doc_id'].unique()

            # Using doctor_ids, find the corresponding doctor names from doctor_df
            consulted_doctors = doctor_df[doctor_df['id'].isin(doctor_ids)]['name'].unique()

            # Find the diseases of the selected patient from patient_history
            patient_diseases = patient_history_df[patient_history_df['pat_id'] == patient_id]['disease'].unique()

            # Display consulted doctors
            if filter_choice == "Doctor":
                st.write(f"Doctors consulted by {selected_patient_name}:")
                if consulted_doctors.size > 0:
                    doctor_name = st.selectbox('Select a doctor:', consulted_doctors)
                    if doctor_name:
                        prescriptions = get_prescriptions_by_doctor(doctor_name, doctor_df, prescription_df, patients_df)
                        st.write(f"Prescriptions by {doctor_name}:")
                        st.table(prescriptions)

                else:
                    st.write(f"No doctors found for {selected_patient_name}.")

            elif filter_choice == "Disease":
                # Display diagnosed diseases
                if patient_diseases.size > 0:
                    disease_name = st.selectbox('Select a disease:', patient_diseases)
                    if disease_name:
                        prescriptions = get_prescriptions_by_disease(disease_name, patient_history_df, prescription_df, patients_df)
                        st.write(f"Prescriptions for {disease_name}:")
                        st.table(prescriptions)
                else:
                    st.write(f"No diseases found for {selected_patient_name}.")

            
        

def ai_patient_profile_page():
    st.title("AI Patient Profile")
    st.write("Select a patient from the dropdown to view AI Profile:")
    
    # Dropdown to select patient_id
    patient_ids = patients_df['patient_id'].unique()
    selected_patient_id = st.selectbox('Choose a Patient ID:', patient_ids)
    
    if selected_patient_id:
        # Call the get_patient_details function
        patient_details_str = get_patient_details(selected_patient_id)
        
        # Print for debugging purposes
        print(patient_details_str)
        
        # Check if patient_details_str is a string
        if isinstance(patient_details_str, str):
            st.write(f"Patient Details for ID: {selected_patient_id}")
            st.write(patient_details_str)
        else:
            st.write("Error: Unable to load patient details. Please check the data source.")


def mail_alert():
    # Button to generate details
    st.title("Trigger Alert")
    st.write("Select a patient from the list below:")
    
    patient_names = patients_df[['first_name', 'last_name']].apply(lambda x: ' '.join(x), axis=1)
    selected_patient_name = st.selectbox('Choose a patient:', patient_names)
    if st.button("Trigger Alert"):
        trigger_alert()
        st.write("Mail Sent!!!")
    # st.write("Mail Sent!!!")


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

def vpg():
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

# Main Page Logic
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "/patient_listing"

    sidebar_content()

    if st.session_state.page == "/patient_listing":
        patient_listing_page()
    elif st.session_state.page == "/patient_details":
        patient_details_page()
    elif st.session_state.page == "/ai_patient_profile":
        ai_patient_profile_page()
    elif st.session_state.page == "/ai_alerts":
        mail_alert()
    elif st.session_state.page == "/voice_prescription":
        vpg()
    

if __name__ == "__main__":
    main()