import mysql.connector
import pandas as pd
import google.generativeai as genai
from datetime import date

def initial():
    genai.configure(api_key='AIzaSyCvHfiUg5GEdqj7BhuZ6VOqcIzgxbbRGu4')

    model = genai.GenerativeModel('gemini-pro')

    prompt_patient_summary ="""

    You need to create patient History Summary for Doctor

    Frequent Occurring Diseases:

    List diseases the patient frequently experiences based on prescription history and reported symptoms.
    Critical Diseases:

    Identify any critical conditions the patient has, noting the severity and recent occurrences.
    Prescription Adherence:

    Evaluate the adherence to prescribed medications. Compare the number of medications that should have been consumed by now versus the actual number taken. Note any discrepancies that suggest non-compliance.
    Age Group:

    Indicate if the patient belongs to an older age group, which might impact their overall health management and prescription adherence.
    Frequently Reported Symptoms:

    Summarize the symptoms that have been reported most frequently by the patient and their recent trends.
    Criticality Flag:

    Highlight any critical issues based on the severity of diseases, non-compliance with prescriptions, or other significant health indicators.
    Example Analysis:

    Diseases: The patient frequently reports hypertension and diabetes. Hypertension was noted in recent visits and is considered critical due to its impact on overall health.
    Critical Diseases: Diabetes is currently poorly controlled, with recent HbA1c levels indicating high risk.
    Prescription Adherence: The patient should have consumed 60 units of blood pressure medication in the past 2 months but has only reported using 40 units. This suggests potential non-compliance.
    Age Group: The patient is 75 years old, which may affect their medication adherence and overall health management.
    Frequently Reported Symptoms: The patient frequently reports dizziness and fatigue, with the latest occurrences happening in the past week.
    Criticality Flag: High – Due to uncontrolled diabetes, significant non-compliance with blood pressure medication, and recent symptoms indicating possible exacerbation of conditions.

    output should be in the form of passage and add allergies as well.

   """
    return model, prompt_patient_summary
def create_db_connection():
    connection = mysql.connector.connect(
        host='apeshackathon.cdqw4626e405.us-east-1.rds.amazonaws.com',
        user='apeshackathon',
        password='apeshackathonpa',
        database='healthcare'
    )
    return connection

def get_gemini_response(model, input_text, user_info=""):
    context = f"User Information:\n{user_info}\n\Task: {input_text}"
    messages = [{"role": "user", "parts": [context]}]

    response = model.generate_content(messages)

    if response.parts:
        return response.parts[0].text
    else:
        return "Sorry, I couldn't generate a response. Please try again."

def get_patient_details(pat_id):
  model, prompt_patient_summary = initial()
  connection = create_db_connection()
  cursor = connection.cursor()
  pat_query = f"""
  SELECT
      p.first_name,
      p.last_name,
      p.age,
      p.gender,
      p.weight,
      p.height,
      p.blood_type,
      p.allergies
  FROM
      patients AS p
  WHERE
      p.patient_id = {pat_id};
  """
  history_query = f"""
  SELECT created_at, investigation, symptoms, summary,disease from patient_history where pat_id = {pat_id};
  """

  pres_query = f"""
  SELECT medicine,created_at,duration,dosage,timing from prescription where patient_id = {pat_id};
  """

  cursor.execute(pat_query)
  df_pres = pd.DataFrame(cursor.fetchall(),columns = ["first name","last name","age","gender","weight","hieght","blood_type","allergies"])

  cursor.execute(history_query)
  df_pat = pd.DataFrame(cursor.fetchall(), columns = ["created_at","investigation","symptom","summary","disease"])

  cursor.execute(pres_query)
  df_hist = pd.DataFrame(cursor.fetchall(),columns = ["medicine","created_at","duration","dosage","timing"])

  pat_det = df_pres.to_dict()
  for row in df_pat.itertuples(index=False):
    if not pat_det.get("history"):
      pat_det['history'] = []
    pat_det["history"].append({
        "investigation": row[1],
        "symptom": row[2],
        "summary": row[3],
        "date": row[0],
        "disease": row[4]
    })
  for row in df_hist.itertuples(index=False):
    if not pat_det.get("prescription"):
      pat_det['prescription'] = []
    pat_det["prescription"].append({
        "medicine": row[0],
        "created_at": row[1],
        "qty": row[2],
        "dosage": row[3],
        "timing": row[4]
    })

  return get_gemini_response(model, prompt_patient_summary, pat_det)


