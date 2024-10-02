import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import date
from diet_plan import generate_diet_plan, generate_recipe_details 
from smart_pres import generate_efficient_details
import re
from symptom import get_diag
import json

# Load CSV data into DataFrames
doctor_df = pd.read_csv('/home/usl-sz-1487/Downloads/Hackathon/Doctor/doctors.csv')
patients_df = pd.read_csv('/home/usl-sz-1487/Downloads/Hackathon/Doctor/patients.csv')
patient_history_df = pd.read_csv('/home/usl-sz-1487/Downloads/Hackathon/Doctor/patient_history_.csv')
prescription_df = pd.read_csv('/home/usl-sz-1487/Downloads/Hackathon/Doctor/prescription.csv')
# Set the API key for the Gemini model
api_key = 'AIzaSyCjVFomXFIO4x4empQQWddFHUIXmX-gDc4'  # Replace with your actual API key
genai.configure(api_key=api_key)

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")
# Define the menu items
menu_items = [
    {"label": "Generate Workout Plan", "icon": "📋", "path": "/generate_workout"},
    {"label": "Generate Diet Plan", "icon": "➕", "path": "/generate_diet"},
    {"label": "Affordable & Understandable", "icon": "🤖", "path": "/affordable"},
    {"label": "Doctor Finder", "icon": "🤖", "path": "/doctor_finder"},
]

# Sidebar content
def sidebar_content():
    st.sidebar.image("https://www.unthinkable.co/wp-content/uploads/2022/08/cropped-footer-logo.webp", width=150)
    st.sidebar.title("Patient Portal")
    
    # Menu items
    for item in menu_items:
        if st.sidebar.button(f"{item['icon']} {item['label']}", key=item['label']):
            st.session_state.page = item['path']

    # Footer
    st.sidebar.markdown("© 2024 Unthinkable Apes")

# Function to get a response from Gemini API
def get_gemini_response(input_text):
    messages = [{"role": "user", "parts": [input_text]}]
    response = genai.GenerativeModel('gemini-pro').generate_content(messages)
    
    # Check if the response has content and return the text
    if response.parts:
        return response.parts[0].text
    else:
        return "Sorry, I couldn't generate a response. Please try again."

def get_workout():
    st.title("Personalized Workout Planner")

    # Personal Information
    st.header("Personal Information")
    name = st.text_input("Name")
    age = st.selectbox("Age", list(range(18, 101)))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    height = st.number_input("Height (cm)", min_value=100, max_value=250)
    weight = st.number_input("Weight (kg)", min_value=30, max_value=300)

    # Workout Goals
    st.header("Workout Goals")
    primary_goal = st.selectbox("Primary Goal", ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility", "Strength"])
    specific_objective = st.text_input("Specific Objective (e.g., lose 5kg, run 5k in 30 minutes)")
    target_date = st.date_input("Target Date", min_value=date.today())

    # Current Workout Level
    st.header("Current Workout Level")
    experience = st.selectbox("Exercise Experience", ["Beginner", "Intermediate", "Advanced"])
    activity_level = st.selectbox("Activity Level", ["Sedentary", "Light Activity", "Moderate", "Active", "Very Active"])
    injuries = st.text_area("Recent Injuries (if any)")
    health_conditions = st.text_area("Health Conditions (if any)")

    # Workout Preferences
    st.header("Workout Preferences")
    preferred_exercise = st.multiselect("Preferred Type of Exercise", ["Cardio", "Strength Training", "HIIT", "Yoga", "Pilates"])
    workout_environment = st.selectbox("Workout Environment", ["Gym", "Home", "Outdoors", "Mixed"])
    equipment = st.multiselect("Preferred Equipment", ["Dumbbells", "Resistance Bands", "Machines", "No Equipment"])
    favorite_exercises = st.text_area("Favorite Exercises")
    disliked_exercises = st.text_area("Disliked Exercises")

    # Schedule Availability
    st.header("Schedule Availability")
    days_available = st.multiselect("Days Available for Workouts", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    time_per_workout = st.selectbox("Time Per Workout", ["30 minutes", "45 minutes", "1 hour", "1.5 hours"])
    preferred_time = st.selectbox("Preferred Time of Day", ["Morning", "Afternoon", "Evening"])

    # Diet and Nutrition
    st.header("Diet and Nutrition")
    diet_type = st.selectbox("Diet Type", ["No Specific Diet", "Vegetarian", "Vegan", "Pescatarian", "Keto", "Paleo"])
    daily_calories = st.number_input("Daily Caloric Intake (if known)", min_value=1000, max_value=5000, step=100)
    macronutrient_preference = st.select_slider("Macronutrient Preference", options=["High Carb", "Balanced", "High Protein", "High Fat"])
    food_restrictions = st.text_area("Food Allergies or Restrictions")

    # Generate Plan Button
    if st.button("Generate Workout Plan"):
        # Compile all inputs into a structured format
        user_info = {
            "Name": name,
            "Age": age,
            "Gender": gender,
            "Height": f"{height} cm",
            "Weight": f"{weight} kg",
            "Primary Goal": primary_goal,
            "Specific Objective": specific_objective,
            "Target Date": target_date,
            "Experience Level": experience,
            "Activity Level": activity_level,
            "Injuries": injuries,
            "Health Conditions": health_conditions,
            "Preferred Exercises": ', '.join(preferred_exercise),
            "Workout Environment": workout_environment,
            "Equipment": ', '.join(equipment),
            "Favorite Exercises": favorite_exercises,
            "Disliked Exercises": disliked_exercises,
            "Days Available": ', '.join(days_available),
            "Time Per Workout": time_per_workout,
            "Preferred Time": preferred_time,
            "Diet Type": diet_type,
            "Daily Calories": daily_calories,
            "Macronutrient Preference": macronutrient_preference,
            "Food Restrictions": food_restrictions,
        }
        
        prompt = f"Based on the following user information, create a personalized Workout plan in tabular form:\n\n{user_info}"
        
        with st.spinner("Generating your personalized Workout plan..."):
            response = get_gemini_response(prompt)
        
        st.subheader("Your Personalized Workout Plan:")
        st.write(response)

def diet_planner():
    # Inject basic custom CSS
    st.markdown("""
        <style>
        .reportview-container {
            background-color: #f5f5f5;
        }
        .sidebar .sidebar-content {
            background-color: #e0e0e0;
        }
        .title {
            color: #ff5722;
            font-size: 2em;
            font-weight: bold;
        }
        .stButton>button {
            color: black;
            border-radius: 5px;
            padding: 10px;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #e64a19;
        }
        .stMarkdown {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Title
    st.title("Custom Diet Plan Generator")

    # Sidebar inputs
    st.header("User Details")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
    height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
    diet_type = st.selectbox("Diet Preference", ["Vegan", "Vegetarian", "Eggitarian", "Non-Vegetarian"])
    goal = st.selectbox("Goal", ["Weight Loss", "Weight Gain"])
    country = st.selectbox("Country", ["USA", "UK", "India", "China", "Japan", "Other"])

    # Generate button
    if st.button("Generate Diet Plan"):
        with st.spinner("Generating diet plan..."):
            try:
                # Generate diet plan and store it in session state
                diet_plan = generate_diet_plan(gender, weight, height, diet_type, goal, country)
                st.session_state.diet_plan = diet_plan

                # Extract meal options for dropdowns
                st.session_state.meal_options = extract_meal_options(diet_plan)
                
                st.success("Diet Plan Generated!")

                # Debug output
                #st.text("Extracted Meal Options:")
                #st.json(st.session_state.meal_options)

            except Exception as e:
                st.error(f"An error occurred: {e}")

    # Display the diet plan if it exists in session state
    if 'diet_plan' in st.session_state:
        st.markdown(st.session_state.diet_plan, unsafe_allow_html=True)

        # Meal selection dropdowns
        meal_type = st.selectbox("Select Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
        if meal_type and 'meal_options' in st.session_state:
            options = st.session_state.meal_options.get(meal_type, [])
            if options:
                selected_meal = st.selectbox(f"Select {meal_type} Option", options)
                if selected_meal:
                    with st.spinner("Generating recipe details..."):
                        try:
                            recipe_details = generate_recipe_details(selected_meal)
                            st.markdown(recipe_details, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"An error occurred while fetching recipe details: {e}")
            else:
                st.warning(f"No options available for {meal_type}")

def extract_meal_options(diet_plan):
    # Initialize an empty dictionary to hold meal options
    meals = {"Breakfast": [], "Lunch": [], "Dinner": [], "Snacks": []}
    
    # Split the diet plan into sections based on meal types
    sections = diet_plan.split('\n\n')  # Assuming double newline separates sections
    
    current_meal_type = None
    
    for section in sections:
        if any(meal_type in section for meal_type in meals.keys()):
            for meal_type in meals.keys():
                if meal_type in section:
                    current_meal_type = meal_type
                    break
        if current_meal_type:
            lines = section.split('\n')
            for line in lines:
                if "Option" in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        option_text = parts[1].strip()

                        # Remove leading '** ' if present
                        if option_text.startswith("** "):
                            option_text = option_text[3:].strip()
   
                        if option_text:
                            meals[current_meal_type].append(option_text)

    return meals


def affordable_page():
    st.title("Affordable & Understandable Medicine Details")
    st.write("Select a patient from the list below:")
    
    # Concatenate first and last names to create full name
    # Create a dropdown to select a patient
    patient_names = patients_df[['first_name', 'last_name']].apply(lambda x: ' '.join(x), axis=1)
    selected_patient_name = st.selectbox('Choose a patient:', patient_names)

    if selected_patient_name:
        # Get the patient_id of the selected patient
        patient_id = patients_df[patients_df.apply(lambda row: ' '.join([row['first_name'], row['last_name']]) == selected_patient_name, axis=1)]['patient_id'].values[0]

        # Get medicine names for the selected patient
        patient_medicines = prescription_df[prescription_df['patient_id'] == patient_id]['medicine']

        # Get disease name for the selected patient from the patient_history DataFrame
        patient_diseases = patient_history_df[patient_history_df['pat_id'] == patient_id]['disease']

        if not patient_medicines.empty and not patient_diseases.empty:
            st.write("Select a medicine and disease from the list below:")
            
            # Combine medicine names with disease names for dropdown
            med_disease_combination = [
                f"{med} (Disease: {disease})" 
                for med, disease in zip(patient_medicines, patient_diseases)
            ]
            
            # Display the combined medicine and disease in a dropdown
            selected_medicine_disease = st.selectbox('Choose a medicine and disease:', med_disease_combination)
        else:
            st.write("No medicines or diseases found for this patient.")

    match = re.search(r'([A-Za-z]+)\s*\d+mg.*Disease:\s*([A-Za-z\s]+)', selected_medicine_disease)

    if match:
        medicine_name = match.group(1)
        disease_name = match.group(2)

    # Button to generate details
    if st.button("Generate Details"):
        if medicine_name or disease_name:
            content = generate_efficient_details(medicine_name, disease_name)
            st.subheader("Generated Details:")
            st.write(content)
        else:
            st.warning("Please enter the names of medicines and diseases to generate details.")



def disease_finder():
    st.title("Doctor Finder")
    
    # Text box for user input
    input_text = st.text_area("Enter symptoms:")
    
    if st.button("Generate"):
        # Call the function to get the diagnosis
        diagnosis_result = get_diag(input_text).replace("```json", "").replace("```", "")
        print(diagnosis_result)
        # Parse the JSON result
        try:
            data = json.loads(diagnosis_result)
            possible_doctors = data.get("possible_doctors", [])
            
            # Convert the list of doctors to a DataFrame
            df = pd.DataFrame(possible_doctors)
            
            # Display the DataFrame as a table
            st.write("Diagnosis Result:")
            st.write(df)
        except json.JSONDecodeError:
            st.error("Failed to decode the diagnosis result.")

        
# Main Page Logic
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "/generate_workout"

    sidebar_content()

    if st.session_state.page == "/generate_workout":
        get_workout()
    elif st.session_state.page == "/generate_diet":
        diet_planner()
    # Updated to use the function you defined
    elif st.session_state.page == "/affordable":
        affordable_page()  # Added functionality for affordable page
    elif st.session_state.page == "/doctor_finder":
        disease_finder() 
if __name__ == "__main__":
    main()