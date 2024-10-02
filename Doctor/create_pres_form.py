import streamlit as st
import pandas as pd
import numpy as np

# Define validation functions
def validate_form(diagnosis, investigation, medicines):
    errors = []
    if not diagnosis:
        errors.append("Diagnosis is required")
    if not investigation:
        errors.append("Investigation is required")
    if not medicines or any(
        not all(
            [medicine.get("type"), medicine.get("name"), medicine.get("dosage"), medicine.get("count"), medicine.get("timing"), medicine.get("timesPerDay"), medicine.get("duration")]
        )
        for medicine in medicines
    ):
        errors.append("All medicine fields are required")
    return errors

# Streamlit UI
st.title("Fill below form to generate Prescription.")

# General Information
st.subheader("General Information")
col1, col2, col3 = st.columns(3)

with col1:
    doctor = st.selectbox("Doctor", ["Doctor 1", "Doctor 2"])
with col2:
    hospital = st.selectbox("Hospital", ["Hospital 1", "Hospital 2"])
with col3:
    patient = st.selectbox("Patient", ["Patient 1", "Patient 2"])

# Tab Switch for Manual/Voice
tab = st.radio("Enter patient symptoms", ["Manual", "Voice"])

if tab == 'Manual':
    st.subheader("Manual Entry")

    # Diagnosis
    diagnosis = st.text_area("Diagnosis", height=100)

    # Investigation
    investigation = st.text_area("Investigation", height=100)

    # Medicines
    st.subheader("RX/Medicine")
    num_medicines = st.number_input("Number of medicines", min_value=1, max_value=10, value=1)

    medicines = []
    for i in range(num_medicines):
        st.write(f"Medicine {i + 1}")
        medicine_type = st.text_input(f"Type {i + 1}", key=f"type_{i}")
        name = st.text_input(f"Name {i + 1}", key=f"name_{i}")
        dosage = st.text_input(f"Dosage {i + 1}", key=f"dosage_{i}")
        count = st.number_input(f"Count {i + 1}", key=f"count_{i}")
        timing = st.text_input(f"Timing {i + 1}", key=f"timing_{i}")
        times_per_day = st.selectbox(f"Times a Day {i + 1}", ["Once", "Twice", "Thrice"], key=f"times_per_day_{i}")
        duration = st.text_input(f"Duration {i + 1}", key=f"duration_{i}")

        medicines.append({
            "type": medicine_type,
            "name": name,
            "dosage": dosage,
            "count": count,
            "timing": timing,
            "timesPerDay": times_per_day,
            "duration": duration
        })

    # Submit Button
    if st.button("Submit"):
        errors = validate_form(diagnosis, investigation, medicines)
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Call API or handle form submission
            st.success("Form submitted successfully!")
            st.write({
                "doctor": doctor,
                "hospital": hospital,
                "patient": patient,
                "diagnosis": diagnosis,
                "investigation": investigation,
                "medicines": medicines
            })