import google.generativeai as genai

def get_diag(symptoms):
  genai.configure(api_key='AIzaSyCvHfiUg5GEdqj7BhuZ6VOqcIzgxbbRGu4')

  model = genai.GenerativeModel('gemini-pro')
  prompt_summ = f"""
  Given the following patient symptoms: {symptoms}, predict the most likely diagnosis. Take into account common conditions, severity, and any possible underlying causes. Provide a diagnosis that matches the patient's symptoms
  in the form of json with key = [possible doctors you should consider visiting]. Rank on the basis of most likely to be the write doctor
  """
  return get_gemini_response(prompt_summ, '')

def get_gemini_response(input_text, user_info=""):
    genai.configure(api_key='AIzaSyCvHfiUg5GEdqj7BhuZ6VOqcIzgxbbRGu4')

    model = genai.GenerativeModel('gemini-pro')
    context = f"User Information:\n{user_info}\n\Task: {input_text}"
    messages = [{"role": "user", "parts": [context]}]

    response = model.generate_content(messages)
    print(response)
    if response.parts:
        return response.parts[0].text
    else:
        return "Sorry, I couldn't generate a response. Please try again."