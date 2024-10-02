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


def create_db_connection():
    connection = mysql.connector.connect(
        host='apeshackathon.cdqw4626e405.us-east-1.rds.amazonaws.com',
        user='apeshackathon',
        password='apeshackathonpa',
        database='healthcare'
    )
    return connection

def get_gemini_response(input_text,user_info):
    genai.configure(api_key='AIzaSyCvHfiUg5GEdqj7BhuZ6VOqcIzgxbbRGu4')
    model = genai.GenerativeModel('gemini-pro')

    context = f"User Information:\n{user_info}\n\Task: {input_text}"
    messages = [{"role": "user", "parts": [context]}]

    response = model.generate_content(messages)

    if response.parts:
        return response.parts[0].text
    else:
        return "Sorry, I couldn't generate a response. Please try again."
def create_alert(row,city):
  if city:
    prompt = f"""You have to act as helpful assistant and create alert for patients to take their medicine. Patient and medication details are provided.
    Please create alerts in english but if city is present then use regional language for eg if city is delhi then send message in hindi, if punjab then in punjabi etc.
    The city is {city}.
    """
  else:
    prompt = "You have to act as helpful assistant and create alert for patients to take their medicine."
  response = get_gemini_response(prompt,row)
  return response

def send_alert(message, phone):
  TWILIO_ACCOUNT_SID = 'ACbe1359276a8b63c9b09e9096c41f5f35'
  TWILIO_AUTH_TOKEN = 'b34db15606fceb57826938dd149f0da0'
  TWILIO_PHONE_NUMBER = '13048734766'
  client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
  print("phone value",phone)
  # Send the message
  message = client.messages.create(
      body=message,
      from_=TWILIO_PHONE_NUMBER,
      to=phone)
  print(message)
  print(f"Message sent to {phone}, SID: {message.sid}")


def trigger_mail(body, reciever='shivam@unthinkable.co'):
  MAIL_SERVER = "smtp.gmail.com"
  MAIL_PORT = 465
  MAIL_USERNAME = "mayank.soni@unthinkable.co"
  MAIL_PASSWORD = "sachisxwqafwxkbs"
  MAIL_USE_TLS = False
  MAIL_USE_SSL = True
  MAIL_DEFAULT_SENDER = "mayank.soni@unthinkable.co"

  # Email content (replace with your actual values)
  subject = "Medicine Alert!!!!"
  body_text = body
  cc = "cc.email@example.com"
  try:
      print(f"Creating mail with subject: {subject}")

      # Create the email message
      message = MIMEMultipart()
      message["From"] = MAIL_DEFAULT_SENDER
      message["To"] = "shivam.yadav@unthinkable.co"
      message["Subject"] = subject

      # Attach the body text to the email
      message.attach(MIMEText(body_text, "plain"))

      print(f"Sending mail with subject: {subject}")

      # Connect to the email server
      with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) as server:
          server.login(MAIL_USERNAME, MAIL_PASSWORD)

          # Convert the message to a string and send it
          text = message.as_string()
          server.sendmail(MAIL_DEFAULT_SENDER, ["shivam.yadav@unthinkable.co"] + cc.split(","), text)

      print("Email sent successfully!")

  except Exception as e:
      print(f"Failed to send email. Error: {str(e)}")

def trigger_alert():
  connection = create_db_connection()
  cursor = connection.cursor()
  query = "select * from prescription;"
  cursor.execute(query)
  result = cursor.fetchall()
  df_pres = pd.DataFrame(result,columns = ["id","patient_id","doc_id","medicine","created_at","updated_at","duration","dosage","timing","med_count","patient_history"])

  query_pat = "select patient_id,first_name,last_name,age,gender,phone_number,city,country from patients;"
  cursor.execute(query_pat)
  result = cursor.fetchall()
  df_pat = pd.DataFrame(result,columns = ["patient_id","first_name","last_name","age","gender","phone_number","city","country"])


  today_datetime = datetime.now()
  today_date = today_datetime.date()
  time_map = {
      "morning": "7:00",
      "lunch": "14:00",
      "evening": "17:00",
      "night": "20:00"
  }

  call_time = "morning" #morning, lunch, evening, night #input

  alert_list = []

  for row in df_pres.itertuples(index=False):

    end_date = row[4]+timedelta(days=row[6])
    if isinstance(end_date, datetime):
          end_date = end_date.date()
    if end_date >= today_date:
        time = row[8].split(",")
        if time_map[call_time] in time:
          alert_list.append(row)

  df_pres = pd.DataFrame(alert_list)
  df_final = pd.merge(df_pres,df_pat,how="left",on="patient_id")
  df_final = df_final.drop(df_final.index[0])
  email_alert = dict()
  for row in df_final.itertuples(index=False):
    if row[15] not in email_alert:
      email_alert[row[15]] = {}
      email_alert[row[15]]["medicine"] = []
      email_alert[row[15]]["pat_det"] = {
          "first_name":row[11],
          "last_name": row[12],
          "gender":row[14],
          "age":row[12],
          "city": row[16]
      }
    email_alert[row[15]]["medicine"].append({
        "medicine": row[3],
        "timing": row[8],
        "medicine_count": row[9]
    })

  alert = {}
  for k,v in email_alert.items():
    alert[k] = create_alert(v,v["pat_det"]["city"])
  print(alert)
  for k,v in alert.items():
    try:
      if not k.startswith("+"):
          k = f"+91{k}"
      send_alert(v,k)
      trigger_mail(v)
    except Exception as e:
      print(str(e))

