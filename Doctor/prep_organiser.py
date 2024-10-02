import pandas as pd

def get_patient_details(patient_id, patients_df, patient_history_df, doctor_df, prescription_df):
    # Filter patient data
    patient_data = patients_df[patients_df['patient_id'] == patient_id]
    
    if patient_data.empty:
        return pd.DataFrame()  # Return an empty DataFrame if patient not found
    
    # Filter related patient history and merge with doctor data
    patient_history_data = patient_history_df[patient_history_df['pat_id'] == patient_id]
    patient_history_with_doctor = pd.merge(patient_history_data, doctor_df, left_on='doc_id', right_on='id', suffixes=('_history', '_doctor'))
    
    # Filter related prescriptions and merge with doctor data
    prescriptions_data = prescription_df[prescription_df['patient_id'] == patient_id]
    prescriptions_with_doctor = pd.merge(prescriptions_data, doctor_df, left_on='doc_id', right_on='id', suffixes=('_prescription', '_doctor'))
    
    # Prepare patient history and prescriptions as separate DataFrames
    patient_history_summary = patient_history_with_doctor[['investigation', 'symptoms', 'summary', 'name']]
    prescriptions_summary = prescriptions_with_doctor[['medicine', 'duration', 'dosage', 'timing', 'med_count', 'name']]
    
    # Combine patient info, history, and prescriptions into a single DataFrame
    patient_info = pd.concat([patient_data] * (len(patient_history_summary) + len(prescriptions_summary)), ignore_index=True)
    
    # Add patient history and prescriptions
    patient_history_summary = patient_history_summary.rename(columns={'name_doctor': 'doctor_name'})
    prescriptions_summary = prescriptions_summary.rename(columns={'name_doctor': 'doctor_name'})
    
    combined_df = pd.concat([patient_info, patient_history_summary, prescriptions_summary], axis=1)
    
    return combined_df


def get_prescriptions_by_doctor(doctor_name, doctor_df, prescription_df, patients_df):
    # Filter doctor data to get the doctor's ID
    doctor_data = doctor_df[doctor_df['name'] == doctor_name]
    
    if doctor_data.empty:
        return pd.DataFrame()  # Return an empty DataFrame if doctor not found
    
    doctor_id = doctor_data['id'].values[0]
    
    # Filter prescriptions data based on doctor ID
    prescriptions_by_doctor = prescription_df[prescription_df['doc_id'] == doctor_id]
    
    if prescriptions_by_doctor.empty:
        return pd.DataFrame()  # Return an empty DataFrame if no prescriptions are found
    
    # Merge prescriptions with patient data
    prescriptions_with_patients = pd.merge(prescriptions_by_doctor, patients_df, left_on='patient_id', right_on='patient_id')
    
    return prescriptions_with_patients



def get_prescriptions_by_disease(disease_name, patient_history_df, prescription_df, patients_df):
    # Filter patient history by disease
    patient_history_data = patient_history_df[patient_history_df['disease'] == disease_name]
    
    if patient_history_data.empty:
        return pd.DataFrame()  # Return an empty DataFrame if no matching disease found
    
    # Get patient IDs and doctor IDs from the filtered patient history
    patient_ids = patient_history_data['pat_id'].unique()
    
    # Filter prescriptions by patient IDs
    prescriptions_data = prescription_df[prescription_df['patient_id'].isin(patient_ids)]
    
    if prescriptions_data.empty:
        return pd.DataFrame()  # Return an empty DataFrame if no matching prescriptions found
    
    # Merge prescriptions with patient data
    prescriptions_with_patients = pd.merge(prescriptions_data, patients_df, left_on='patient_id', right_on='patient_id')
    
    return prescriptions_with_patients





# def get_prescriptions_by_disease(disease_name, patient_history_df, prescription_df, patients_df):
#     # Filter patient history by disease
#     patient_history_data = patient_history_df[patient_history_df['disease'] == disease_name]
    
#     if patient_history_data.empty:
#         return pd.DataFrame()  # Return an empty DataFrame if no matching disease found
    
#     # Get patient IDs from the filtered patient history
#     patient_ids = patient_history_data['pat_id'].unique()
    
#     # Filter prescriptions by patient IDs
#     prescriptions_data = prescription_df[prescription_df['patient_id'].isin(patient_ids)]
    
#     if prescriptions_data.empty:
#         return pd.DataFrame()  # Return an empty DataFrame if no matching prescriptions found
    
#     # Merge prescriptions with patient data
#     prescriptions_with_patients = pd.merge(prescriptions_data, patients_df, left_on='patient_id', right_on='patient_id')
    
#     # Merge the result with patient history to include disease information
#     final_result = pd.merge(prescriptions_with_patients, patient_history_data[['pat_id', 'disease']], on='patient_id')
    
#     # Drop duplicate columns if any
#     final_result = final_result.loc[:,~final_result.columns.duplicated()]
    
#     return final_result
