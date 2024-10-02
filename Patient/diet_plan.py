import google.generativeai as genai
from google.generativeai.types import GenerationConfig


def generate_diet_plan(gender, weight, height, diet_type, goal, country):
    api_key = 'AIzaSyCjVFomXFIO4x4empQQWddFHUIXmX-gDc4'  # Replace with your actual API key
    genai.configure(api_key=api_key)

    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        f"Generate a comprehensive and visually appealing diet plan tailored to the following specifications:\n"
        f"- **Goal:** {goal}\n"
        f"- **Gender:** {gender}\n"
        f"- **Height:** {height} cm\n"
        f"- **Weight:** {weight} kg\n"
        f"- **Country:** {country}\n"
        f"- **Diet Type:** {diet_type}\n\n"
        f"The diet plan should include:\n"
        f"- **Breakfast:** Provide meal options with approximate calorie counts and brief nutritional information.\n"
        f"- **Lunch:** Include diverse meal options, calorie counts, and essential nutritional details.\n"
        f"- **Dinner:** Suggest various meals with calorie estimates and nutritional breakdown.\n"
        f"- **Snacks:** Offer snack choices with calorie information and key nutritional insights.\n\n"
        f"Format the plan with clear headings for each meal type, bullet points for options, and sections for nutritional information. "
        f"Ensure that the recommendations are suitable for a {diet_type} diet and consider regional dietary preferences relevant to {country}."
    )
    response = model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            max_output_tokens=1500,
            temperature=0.7,
        )
    )
    return response.text


def generate_recipe_details(meal_name):
    api_key = 'AIzaSyCjVFomXFIO4x4empQQWddFHUIXmX-gDc4'  # Replace with your actual API key
    genai.configure(api_key=api_key)

    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = (
        f"Provide a comprehensive recipe for {meal_name}. The recipe should include:\n\n"
        f"1. **Ingredients**: List all the ingredients with their quantities. Include measurements in standard units (e.g., grams, liters, cups).\n\n"
        f"2. **Cooking Instructions**: Provide step-by-step instructions on how to prepare and cook the dish. Use clear and concise language, and include any specific techniques or tips.\n\n"
        f"3. **Cooking Time**: Specify the total cooking time, including preparation and cooking times.\n\n"
        f"4. **Nutritional Information**: Include a breakdown of key nutrients per serving (e.g., calories, protein, carbohydrates, fat, fiber, vitamins, and minerals).\n\n"
        f"5. **Image**: Provide a high-quality image of the finished dish, if possible. (If not possible, mention that no image is available.)\n\n"
        f"6. **Serving Size**: Indicate the recommended serving size and the number of servings the recipe makes.\n\n"
        f"Format the response with clear headings for each section, and use bullet points or numbered lists for ingredients and steps. Ensure that the recipe is easy to follow and provides all necessary information for someone to recreate the dish accurately."
    )
    response = model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            max_output_tokens=1500,  # Adjusted to allow for more detailed responses
            temperature=0.7,
        )
    )
    return response.text

