from flask import Flask, request, jsonify
import google.generativeai as genai
from datetime import date

# Initialize Flask app
app = Flask(__name__)

# Configure the Gemini API (replace with your actual API key)
genai.configure(api_key='AIzaSyCvHfiUg5GEdqj7BhuZ6VOqcIzgxbbRGu4')

# Function to get a response from Gemini API
def get_gemini_response(input_text):
    messages = [{"role": "user", "parts": [input_text]}]
    response = genai.GenerativeModel('gemini-pro').generate_content(messages)
    
    # Check if the response has content and return the text
    if response.parts:
        return response.parts[0].text
    else:
        return "Sorry, I couldn't generate a response. Please try again."

# API Route to get Workout plan
@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    # Get user data from POST request
    pat_det_query = f"select first_name, age, gender, height, weight from patients where patient_id=1"
    cursor.execute(pat_det_query)
    result = cursor.fetchall()
    first_name = result[0]["first_name"]
    age = result[0]["age"]
    gender = result[0]["gender"]
    height = result[0]["height"]
    weight = result[0]["weight"]
    
    data = request.json
    
    primary_goal = data.get('primary_goal')
    specific_objective = data.get('specific_objective')
    target_date = data.get('target_date', str(date.today()))
    experience = data.get('experience')
    activity_level = data.get('activity_level')
    injuries = data.get('injuries')
    health_conditions = data.get('health_conditions')
    preferred_exercises = data.get('preferred_exercises', [])
    workout_environment = data.get('workout_environment')
    equipment = data.get('equipment', [])
    favorite_exercises = data.get('favorite_exercises')
    disliked_exercises = data.get('disliked_exercises')
    days_available = data.get('days_available', [])
    time_per_workout = data.get('time_per_workout')
    preferred_time = data.get('preferred_time')
    diet_type = data.get('diet_type')
    daily_calories = data.get('daily_calories')
    macronutrient_preference = data.get('macronutrient_preference')
    food_restrictions = data.get('food_restrictions')

    # Compile user information into a structured format
    user_info = f"""
    Name: {name}
    Age: {age}
    Gender: {gender}
    Height: {height} 
    Weight: {weight} 
    Primary Goal: {primary_goal}
    Specific Objective: {specific_objective}
    Target Date: {target_date}
    Experience Level: {experience}
    Activity Level: {activity_level}
    Injuries: {injuries}
    Health Conditions: {health_conditions}
    Preferred Exercises: {', '.join(preferred_exercises)}
    Workout Environment: {workout_environment}
    Equipment: {', '.join(equipment)}
    Favorite Exercises: {favorite_exercises}
    Disliked Exercises: {disliked_exercises}
    Days Available: {', '.join(days_available)}
    Time Per Workout: {time_per_workout}
    Preferred Time: {preferred_time}
    Diet Type: {diet_type}
    Daily Calories: {daily_calories}
    Macronutrient Preference: {macronutrient_preference}
    Food Restrictions: {food_restrictions}
    """
    
    prompt = f"Based on the following user information, create a personalized Workout plan in tabular form:\n\n{user_info}"
    
    # Get response from Gemini API
    response = get_gemini_response(prompt)
    
    return jsonify({"Workout_plan": response})

# API Route to generate HTML and CSS based on the Workout plan
@app.route('/generate_html_css', methods=['POST'])
def generate_html_css():
    data = request.json
    Workout_plan = data.get('Workout_plan')

    prompt = f"""
    Convert the following content into complete HTML and CSS code:
    
    {Workout_plan}

    - The HTML should include all necessary tags (e.g., <!DOCTYPE html>, <html>, <head>, <body>).
    - The page background should be light gray (#f0f0f0).
    - Text should be easy to read, using Arial or sans-serif fonts.
    - Add padding and margins for clean spacing.
    - Ensure the layout is responsive and works well on all screen sizes.
    """

    # Get response from Gemini API
    response = get_gemini_response(prompt)
    
    return jsonify({"html_css_code": response})

# Start Flask app
if __name__ == '__main__':
    app.run(debug=True)
