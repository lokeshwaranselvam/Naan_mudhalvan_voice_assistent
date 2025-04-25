import requests
import speech_recognition as sr
import pyttsx3

from flask import Flask, render_template, jsonify
import threading

app = Flask(__name__, template_folder='test')

# ✅ Your Hugging Face API Token
HUGGINGFACE_API_KEY = "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"

# 🎤 Speech recognizer and TTS
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

def speak(text):
    print(f"🤖 Assistant: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            query = recognizer.recognize_google(audio)
            print(f"🗣️ You said: {query}")
            return query
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

# ✅ Use mistralai/Mixtral-8x7B-Instruct-v0.1 (free, powerful)
def ask_huggingface(question):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": f"<s>[INST] {question} [/INST]",
        "parameters": {"max_new_tokens": 100}
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and "generated_text" in result[0]:
                return result[0]["generated_text"]
            return str(result)
        else:
            return f"❌ Hugging Face Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"⚠️ Error: {e}"

# 🔁 Endpoint for voice command
@app.route('/voice-command', methods=['POST'])
def voice_command():
    query = listen()
    if query:
        if "exit" in query.lower() or "stop" in query.lower():
            speak_thread = threading.Thread(target=speak, args=("Goodbye!",))
            speak_thread.start()
            return jsonify({'command': 'Goodbye!'})

        response = ask_huggingface(query)
        speak_thread = threading.Thread(target=speak, args=(response,))
        speak_thread.start()
        return jsonify({'command': response})

    return jsonify({'command': 'Sorry, I didn\'t catch that.'})

# 🌐 Render frontend
@app.route('/')
def index():
    return render_template('frontend_v/oice_assistant.html')

if __name__ == "__main__":
    app.run(debug=True)
