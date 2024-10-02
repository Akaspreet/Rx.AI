import os
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment

def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(audio_file)
    wav_file = "temp.wav"
    audio.export(wav_file, format="wav")
    with sr.AudioFile(wav_file) as source:
        audio_data = recognizer.record(source)
    transcription = recognizer.recognize_google(audio_data)
    os.remove(wav_file)
    return transcription

def text_to_speech(input_text, lang='en'):
    tts = gTTS(text=input_text, lang=lang)
    speech_file = "output.mp3"
    tts.save(speech_file)
    return speech_file
