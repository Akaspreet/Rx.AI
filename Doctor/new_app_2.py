from flask import Flask, request, jsonify, send_file
from modules.audio_processing import speech_to_text, text_to_speech
from modules.translation import translate_text, summarize_text
from modules.gemini_api import generate_text
from analysis import analyze_conversation, format_medication
import io
import numpy as np
import scipy.io.wavfile as wav

app = Flask(__name__)

# Language options
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Russian": "ru",
    "Chinese (Simplified)": "zh-cn",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Turkish": "tr",
    "Swedish": "sv",
    "Danish": "da",
    "Hindi": "hi"
}


# Function to save audio to a BytesIO object
def save_wav_to_bytesio(audio_data, sample_rate):
    temp_file = io.BytesIO()
    wav.write(temp_file, sample_rate, (audio_data * 32767).astype(np.int16))  # Convert float32 to int16
    temp_file.seek(0)  # Rewind the BytesIO object
    return temp_file


@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({"error": "No audio file provided."}), 400
    
    # Save the audio data
    temp_file = io.BytesIO(audio_file.read())
    return jsonify({"message": "Audio uploaded successfully", "audio_file": temp_file.getvalue()})


@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({"error": "No audio file provided."}), 400

    transcription = speech_to_text(audio_file)
    
    # Perform analysis
    analysis_result = analyze_conversation(transcription)
    
    formatted_result = {
        "disease": analysis_result.get("disease", ""),
        "medications": [format_medication(med) for med in analysis_result.get("medications", [])],
        "next_checkup": analysis_result.get("next_checkup", ""),
        "investigations": analysis_result.get("additional_tests", [])
    }

    return jsonify({
        "transcription": transcription,
        "analysis_result": formatted_result
    })


@app.route('/translate_text', methods=['POST'])
def translate_text_route():
    data = request.json
    transcription = data.get('transcription')
    target_lang = data.get('language')

    if not transcription or not target_lang:
        return jsonify({"error": "Missing transcription or language data."}), 400

    if target_lang not in LANGUAGES:
        return jsonify({"error": "Invalid target language."}), 400

    translated_text = translate_text(transcription, LANGUAGES[target_lang])
    return jsonify({"translated_text": translated_text})


@app.route('/summarize_text', methods=['POST'])
def summarize_text_route():
    data = request.json
    transcription = data.get('transcription')

    if not transcription:
        return jsonify({"error": "Missing transcription."}), 400

    summary = summarize_text(transcription)
    return jsonify({"summary": summary})


@app.route('/play_translated_audio', methods=['POST'])
def play_translated_audio():
    data = request.json
    translated_text = data.get('translated_text')
    lang = data.get('language')

    if not translated_text or not lang:
        return jsonify({"error": "Missing translated text or language data."}), 400

    if lang not in LANGUAGES:
        return jsonify({"error": "Invalid language."}), 400

    audio_data = text_to_speech(translated_text, lang=LANGUAGES[lang])

    return send_file(
        io.BytesIO(audio_data),
        mimetype='audio/wav',
        as_attachment=True,
        download_name='translated_audio.wav'
    )


if __name__ == '__main__':
    app.run(debug=True)
