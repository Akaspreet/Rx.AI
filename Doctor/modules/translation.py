from googletrans import Translator
from transformers import pipeline
from deep_translator import GoogleTranslator
from langdetect import detect,DetectorFactory

# Ensure consistent language detection results
DetectorFactory.seed = 0

def translate_text(text, target_lang='en'):
    try:
        # Translate the text to the target language
        source_lang = detect(text)
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated_text = translator.translate(text)
        return translated_text
    except Exception as e:
        print(f"Error during translation: {e}")
        return "Translation error"

def summarize_text(text):
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    summary = summarizer(text,truncation=True, max_length=len(text), do_sample=False,clean_up_tokenization_spaces=False)
    return summary[0]['summary_text']



