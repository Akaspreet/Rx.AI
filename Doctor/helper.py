# import speech_recognition as sr
# from pydub import AudioSegment
# import google.generativeai as genai
# from datetime import date
# from datetime import datetime
# import mysql.connector

# def create_db_connection():
#     connection = mysql.connector.connect(
#         host='apeshackathon.cdqw4626e405.us-east-1.rds.amazonaws.com',
#         user='apeshackathon',
#         password='apeshackathonpa',
#         database='healthcare'
#     )
#     return connection

# genai.configure(api_key='AIzaSyCvHfiUg5GEdqj7BhuZ6VOqcIzgxbbRGu4')

# model = genai.GenerativeModel('gemini-pro')
# def get_gemini_response(input_text,user_info):
#     context = f"User Information:\n{user_info}\n\Task: {input_text}"
#     messages = [{"role": "user", "parts": [context]}]

#     response = model.generate_content(messages)

#     if response.parts:
#         return response.parts[0].text
#     else:
#         return "Sorry, I couldn't generate a response. Please try again."
    

# def convert_wav_to_text(wav_file_path):
#     # Initialize recognizer
#     recognizer = sr.Recognizer()

#     # Load the wav file
#     audio = AudioSegment.from_wav(wav_file_path)
#     wav_file_path = "recording.wav"
#     audio.export(wav_file_path, format="wav")

#     # Read the audio file
#     with sr.AudioFile(wav_file_path) as source:
#         audio_data = recognizer.record(source)
#         try:
#             # Convert audio to text
#             text = recognizer.recognize_google(audio_data)
#             print("Transcription: " + text)
#         except sr.UnknownValueError:
#             print("Google Speech Recognition could not understand audio.")
#         except sr.RequestError as e:
#             print(f"Could not request results from Google Speech Recognition service; {e}")

#     return text

# def extract_data(text):
#     prompt = """
#     You are provided with an audio recording between patient and doctor. Doctor is mentioning the patients diagonosis summary, Disease predicted
#     and medicine prescription. 
#     Try to extract following information about medicine name, duration in days, dosage in mg timinig and medicine count in a single go.
#     The output should in following json format.
#     {
#     'summary': // Everything the doctor said,
#     'disease': //disease predicted for patient,
#     prescription:[
#         'medicine': //medicine name,
#         'duration': //duration in days,
#         'dosage': //dosage in mg 
#         'timinig', //classify whatever time is mentioned for disaese into either 7:00, 14:00. 17:00,20:00 timestampt.They can be multiple so have a string with comma seprated
#         'med_count': //medicine count in a single go,
#     ]
    
#     Add null if info is not present. Following is the conversation between doctor and patient./n
#     """

#     conversation = "Transcription: I think you have cancer and you should take Dolo 3 times a day and paracetamol in morning and evening"
#     res = get_gemini_response(prompt+conversation,'')
#     return res

# def save_in_db(his,prec):
#     for p in prec:
#         pres_query = f"""" 
#         INSERT INTO prescription (patient_id,doc_id,medicine,created_at,duration,dosage,timing,med_count)
#         VALUES (1, 101, {p.get('medicine')},{datetime.now().today()},{p.get('duration')},{p.get('timing')},{p.get('med_count')});
#         """
#         connection = create_db_connection()
#         cur = connection.cursor()
#         cur.execute(pres_query)
#         cur.commit()

#     his_query = f"""
#     INSERT INTO patient_history (pat_id,doc_id,created_at,investigation,symptoms,disease)
#         VALUES (1, 101,{datetime.now().today()},{his.get('investigation')},{his.get('symptoms')},{his.get('disease')});
#     """
#     connection = create_db_connection()
#     cur = connection.cursor()
#     cur.execute(his_query)
#     cur.commit()


# # Example usageyour_audio_file.wav
# wav_file_path = "recording.wav"
# text_output = convert_wav_to_text(wav_file_path)



# helper.py

import speech_recognition as sr
from pydub import AudioSegment
import google.generativeai as genai
from datetime import datetime
import mysql.connector

def create_db_connection():
    connection = mysql.connector.connect(
        host='apeshackathon.cdqw4626e405.us-east-1.rds.amazonaws.com',
        user='apeshackathon',
        password='apeshackathonpa',
        database='healthcare'
    )
    return connection

genai.configure(api_key='AIzaSyCvHfiUg5GEdqj7BhuZ6VOqcIzgxbbRGu4')

model = genai.GenerativeModel('gemini-pro')

def get_gemini_response(input_text, user_info):
    context = f"User Information:\n{user_info}\n\Task: {input_text}"
    messages = [{"role": "user", "parts": [context]}]

    response = model.generate_content(messages)

    if response.parts:
        return response.parts[0].text
    else:
        return "Sorry, I couldn't generate a response. Please try again."

def convert_wav_to_text(wav_file_path):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_wav(wav_file_path)
    wav_file_path = "recording.wav"
    audio.export(wav_file_path, format="wav")

    with sr.AudioFile(wav_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            print("Transcription: " + text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    return text

def extract_data(text):
    prompt = """
    You are provided with an audio recording between patient and doctor. Doctor is mentioning the patients diagnosis summary, Disease predicted
    and medicine prescription. 
    Try to extract following information about medicine name, duration in days, dosage in mg timing and medicine count in a single go.
    The output should in following json format.
    {
    'summary': // Everything the doctor said,
    'disease': //disease predicted for patient,
    prescription:[
        'medicine': //medicine name,
        'duration': //duration in days,
        'dosage': //dosage in mg 
        'timing', //classify whatever time is mentioned for disease into either 7:00, 14:00. 17:00,20:00 timestamp.They can be multiple so have a string with comma separated
        'med_count': //medicine count in a single go,
    ]
    
    Add null if info is not present. Following is the conversation between doctor and patient./n
    """

    conversation = f"Transcription: {text}"
    res = get_gemini_response(prompt + conversation, '')
    return res

def save_in_db(final_res,res):
    try:
        connection = create_db_connection()
        cursor = connection.cursor()
        
        final_res.get("disease")
        final_res.get("investigation")
        # Insert into patient_history table
        history_query = """
        INSERT INTO patient_history (pat_id, doc_id, created_at, investigation, symptoms, summary, disease)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        history_values = (
            1,  # pat_id (you may want to make this dynamic)
            101,  # doc_id (you may want to make this dynamic)
            datetime.now(),
            ','.join(final_res.get('investigations', [])),
            '',
            res,
            final_res.get('disease', '')
        )
        cursor.execute(history_query, history_values)

        # Insert into prescription table
        for medication in final_res.get('medications', []):
            
            prescription_query = """
            INSERT INTO prescription (patient_id, doc_id, medicine, created_at, duration, dosage, timing, med_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            print(prescription_query)
            prescription_values = (
                1,  # patient_id (you may want to make this dynamic)timing
                101,  # doc_id (you may want to make this dynamic)
                medication.get('medicine', ''),
                datetime.now(),
                medication.get('duration', ''),
                medication.get('dosage', ''),
                ','.join(medication.get('timing', [])),
                medication.get('med_count', '')
            )
            cursor.execute(prescription_query, prescription_values)

        connection.commit()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Example usage
wav_file_path = "recording.wav"
text_output = convert_wav_to_text(wav_file_path)
