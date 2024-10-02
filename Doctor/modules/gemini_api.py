from transformers import pipeline

def load_text_generation_model():
    # Load the text generation model (GPT-2 in this case)
    return pipeline("text-generation", model="gpt2")

def generate_text(prompt, max_length=100):
    # Generate text based on the prompt
    generator = load_text_generation_model()
    result = generator(prompt, max_length=max_length, num_return_sequences=1)
    return result[0]['generated_text']
