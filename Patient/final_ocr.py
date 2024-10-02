from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import re
import pandas as pd
import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

# Set the API key for the Gemini model
api_key = 'AIzaSyCjVFomXFIO4x4empQQWddFHUIXmX-gDc4'  # Replace with your actual API key
genai.configure(api_key=api_key)

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_pdf(pdf_path):
    # Convert PDF pages to images
    images = convert_from_path(pdf_path)

    # Extract text from all pages
    extracted_text = ""
    for page_number, image in enumerate(images, start=1):
        # Use pytesseract to do OCR on each image (PDF page)
        text = pytesseract.image_to_string(image)
        extracted_text += f"{text}"

    return extracted_text

def parse_medicine_details(medicine_text):
    # Improved regex to handle 'Once a day', 'Twice daily', etc.
    medicine_pattern = re.compile(
        r'(\w+)\s*(\d+ mg)\s*(\d+)\s*unit\s*(Before meals|After meals)\s*(Once a day|Twice daily|Thrice daily|Every \d+ hours)\s*(\d+)\s*days',
        re.IGNORECASE
    )
    
    match = medicine_pattern.search(medicine_text)
    if match:
        # Extract medicine details from regex groups
        med_name = match.group(1)  # Medicine Name
        dosage = match.group(2)     # Dosage (e.g., 100 mg)
        med_count = match.group(3)  # Medicine Count (e.g., 1 unit)
        meal_timing = match.group(4) # Meal timing (Before/After meals)
        timing = match.group(5)     # Timing (Once a day, Twice daily, etc.)
        duration = match.group(6)   # Duration in days
        
        return {
            "medicine_name": med_name,
            "medtype": "Tab.",  # Assuming tablet for now
            "dosage": dosage,
            "med_count": med_count,
            "meal_timing": meal_timing,
            "timing": timing,
            "duration": f"{duration} days"
        }
    else:
        return None

def extract_details_from_text(extracted_text):
    # Extract Date
    date = re.search(r'Date:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})', extracted_text)
    date = date.group(1) if date else None

    # Extract Hospital Name
    hospital_name = re.search(r'([A-Za-z\s]+Hospital)', extracted_text)
    hospital_name = hospital_name.group(1) if hospital_name else None

    # Extract Doctor Name
    doctor_name = re.search(r'Dr\.\s*([A-Za-z\s]+)', extracted_text)
    doctor_name = doctor_name.group(1).strip() if doctor_name else None

    # Extract Doctor Qualification
    doctor_qualification = re.search(r'\((MBBS|MD|DO)\)', extracted_text)
    doctor_qualification = doctor_qualification.group(1) if doctor_qualification else None

    # Extract Patient Name (Remove 'Age' from the result)
    patient_name = re.search(r'Patient\s*:\s*([A-Za-z\s]+)\n', extracted_text)
    patient_name = patient_name.group(1).strip() if patient_name else None

    # Extract Patient Age
    age = re.search(r'Age:\s*(\d+)', extracted_text)
    age = age.group(1) if age else None

    # Extract Patient Gender
    gender = re.search(r'Gender:\s*(\w+)', extracted_text)
    gender = gender.group(1) if gender else None

    # Extract Patient Address (City)
    address = re.search(r'City\s*:\s*([A-Za-z\s]+)', extracted_text)
    address = address.group(1).strip() if address else None

    # Extract Patient Mobile Number
    patient_mobile = re.search(r'(\d{10})', extracted_text)
    patient_mobile = patient_mobile.group(1) if patient_mobile else None

    # Extract Height and Weight
    height = re.search(r'Height:\s*(\d+)\s*cm', extracted_text)
    height = height.group(1) if height else None

    weight = re.search(r'Weight:\s*(\d+)\s*kg', extracted_text)
    weight = weight.group(1) if weight else None

    # Extract Diagnosis (Remove 'Ss' from the result)
    diagnosis = re.search(r'Diagnosis:\s*([A-Za-z\s]+)', extracted_text)
    diagnosis = diagnosis.group(1).strip() if diagnosis else None
    diagnosis = diagnosis.replace("Ss", "").strip()  # Remove "Ss"

    # Extract Medicines
    medicines = re.findall(r'¢\s*Tab\.\s*([^\n]+)', extracted_text)
    parsed_medicines = [parse_medicine_details(medicine) for medicine in medicines if parse_medicine_details(medicine)]

    # Extract Investigations (Remove 'Made by Prescription Maker' part)
    investigations = re.search(r'Investigations\s*([\w\s]+)\n', extracted_text)
    investigations = investigations.group(1).strip() if investigations else None

    # Clean 'Made by Prescription Maker' from investigations
    if investigations:
        investigations = re.sub(r'Made by Prescription Maker[\s\S]*', '', investigations).strip()

    # Return the extracted details as a list of dictionaries
    return {
        "Date": date,
        "Hospital Name": hospital_name,
        "Doctor Name": doctor_name,
        "Doctor Qualification": doctor_qualification,
        "Patient Name": patient_name,
        "Patient Age": age,
        "Patient Gender": gender,
        "Patient Address": address,
        "Patient Mobile": patient_mobile,
        "Height (cm)": height,
        "Weight (kg)": weight,
        "Diagnosis": diagnosis,
        "Medicines": parsed_medicines,  # List of parsed medicines
        "Investigations": investigations,
    }

def prepare_final_rows(data):
    # Prepare final rows for backend with medicine details split into individual rows
    rows = []
    for medicine in data['Medicines']:
        row = {
            "Date": data['Date'],
            "Hospital Name": data['Hospital Name'],
            "Doctor Name": data['Doctor Name'],
            "Doctor Qualification": data['Doctor Qualification'],
            "Patient Name": data['Patient Name'],
            "Patient Age": data['Patient Age'],
            "Patient Gender": data['Patient Gender'],
            "Patient Address": data['Patient Address'],
            "Patient Mobile": data['Patient Mobile'],
            "Height (cm)": data['Height (cm)'],
            "Weight (kg)": data['Weight (kg)'],
            "Diagnosis": data['Diagnosis'],
            **medicine,  # Add the medicine details here
            "Investigations": data['Investigations'],
        }
        rows.append(row)

    return rows

def process_pdf_for_backend(pdf_path):
    # Extract text from PDF
    extracted_text = extract_text_from_pdf(pdf_path)

    # Extract details from the text
    data = extract_details_from_text(extracted_text)

    # Prepare final rows of data for backend
    final_rows = prepare_final_rows(data)
    
    return final_rows  # Return the data to be used by backend for SQL or API call

def creating_dataframes(final_data):
    
    # Create Doctor DataFrame
    doctor_df = pd.DataFrame({
        'Doctor Name': [entry['Doctor Name'] for entry in final_data],
        'Doctor Qualification': [entry['Doctor Qualification'] for entry in final_data],
        'Hospital Name': [entry['Hospital Name'].strip() for entry in final_data]
    })

    # Create Patient DataFrame
    patient_df = pd.DataFrame({
        'Patient Name': [entry['Patient Name'] for entry in final_data],
        'Patient Age': [entry['Patient Age'] for entry in final_data],
        'Patient Gender': [entry['Patient Gender'] for entry in final_data],
        'Patient Address': [entry['Patient Address'] for entry in final_data],
        'Patient Mobile': [entry['Patient Mobile'] for entry in final_data],
        'Height (cm)': [entry['Height (cm)'] for entry in final_data],
        'Weight (kg)': [entry['Weight (kg)'] for entry in final_data]
    })

    # Create Patient History DataFrame
    patient_history_df = pd.DataFrame({
        'Diagnosis': [entry['Diagnosis'] for entry in final_data],
        'Investigations': [entry['Investigations'] for entry in final_data]
    })

    # Create Prescription DataFrame
    prescription_df = pd.DataFrame({
        'medicine_name': [entry['medicine_name'] for entry in final_data],
        'medtype': [entry['medtype'] for entry in final_data],
        'dosage': [entry['dosage'] for entry in final_data],
        'med_count': [entry['med_count'] for entry in final_data],
        'meal_timing': [entry['meal_timing'] for entry in final_data],
        'timing': [entry['timing'] for entry in final_data],
        'duration': [entry['duration'] for entry in final_data]
    })

    # Display the DataFrames
    print(doctor_df)
    print(patient_df)
    print(patient_history_df)
    print(prescription_df)

    return doctor_df, patient_df, patient_history_df, prescription_df


if __name__ == "__main__":
    # User input for PDF path
    pdf_path = input("Enter the PDF file path: ")

    # Process the PDF and get the final rows for backend
    final_data = process_pdf_for_backend(pdf_path)
    
    # print("Final data ready for backend:", final_data)

    doctor_df, patient_df, patient_history_df, prescription_df = creating_dataframes(final_data)