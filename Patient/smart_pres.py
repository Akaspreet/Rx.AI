import google.generativeai as genai
from google.generativeai.types import GenerationConfig

# Load API key from environment variable for security
api_key = 'AIzaSyCjVFomXFIO4x4empQQWddFHUIXmX-gDc4'

# Set the API key for the Gemini model
genai.configure(api_key=api_key)

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-pro")

def generate_efficient_details(medicine_name, disease_name):
    # Load API key from environment variable for security
    api_key = 'AIzaSyCjVFomXFIO4x4empQQWddFHUIXmX-gDc4'

    # Set the API key for the Gemini model
    genai.configure(api_key=api_key)

    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"""
    You are a highly knowledgeable medical assistant specializing in providing precise and clear information on medications. I have a prescription medicine and a specific disease that I need more information about. Provide detailed and structured answers to the following:

    1. **Medicine Name**: {medicine_name}
    2. **Disease**: {disease_name}

    Please provide:
    - **Use of this medicine**: Describe how this medicine is used, including its primary purpose in treating the given disease, and explain why it is recommended for this condition.
    - **Allergies and side effects**: List common allergies or side effects that patients should be aware of when taking this medicine.
    - **Generic salt**: Provide the generic salt or active ingredient contained in this medicine.
    - **Alternative medicines**: Provide a list of alternative medicines with the same or similar composition and their prices in Indian Rupees. Include the names, compositions, and approximate costs for each alternative.

    Ensure the information is fact-based, clearly structured, and patient-friendly.
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config=GenerationConfig(
                max_output_tokens=2000,
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e:
        return "An error occurred while generating the details."

def main():
    """
    Main function to interact with the user and generate prescription details.
    """
    try:
        medicine_name = input("Enter the medicine name: ")
        disease_name = input("Enter the disease name: ")

        # Generate structured details
        content = generate_efficient_details(medicine_name, disease_name)
        
        print(f"Prescription details:\n{content}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the program
if __name__ == "__main__":
    main()
