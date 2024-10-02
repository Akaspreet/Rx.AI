# analysis.py
import google.generativeai as genai
import json
import re

# Configure the Gemini API
genai.configure(api_key='AIzaSyCvHfiUg5GEdqj7BhuZ6VOqcIzgxbbRGu4')

def analyze_conversation(conversation):
    # Set up the model
    model = genai.GenerativeModel('gemini-pro')

    # Prepare the prompt
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
                "frequency": '''How often should the medicine be taken?
                            Options:
                            - Once a day
                            - Twice a day
                            - Thrice a day
                            - Four times a day
                            - Once in the morning
                            - Once in the afternoon
                            - Once in the evening
                            - Once at night
                            - Twice after the afternoon

                            If you choose:
                            - Twice a day: The times will be [7:00, 17:00] (morning and evening).
                            - Thrice a day: The times will be [7:00, 14:00, 20:00] (morning, afternoon, and night).
                            - Four times a day: The times will be [7:00, 14:00, 17:00, 20:00] (morning, afternoon, evening, and night).
                            - Once a day: You can select any of these times: [7:00, 14:00, 17:00, or 20:00].
                            - Once in the morning: The time will be 7:00.
                            - Once in the afternoon: The time will be 14:00.
                            - Once in the evening: The time will be 17:00.
                            - Once at night: The time will be 20:00.
                            - Twice after the afternoon: The times will be [17:00, 20:00] (evening and night).
                            
                            
                            show the respective value that is given in list format specifically timing and you have to return only that
                            if twice a day so simply return [7:00, 17:00] just like that.
                            
                            '''

,
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

    # Generate the response
    response = model.generate_content(prompt)

    # Extract JSON from the response
    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group())
            return result
        except json.JSONDecodeError:
            print("Error: Unable to parse JSON response")
            return None
    else:
        print("Error: No JSON found in the response")
        return None

def format_medication(med):
    return {
        "medicine": med['name'],
        # "medtype": med['type'],
        "dosage": med['dosage'],
        "med_count": med['count'],
        "timing": med['frequency'],
        "duration": med['duration'],
        # "meal_timing": med['meal_relation'] if 'before' in med['meal_relation'].lower() else "after meal"
    }
