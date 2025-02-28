from flask import Flask, render_template, request, jsonify
import requests
import config
import google.generativeai as genai
import random
app = Flask(__name__)

genai.configure(api_key=config.api_key)

# ElevenLabs API details
ELEVENLABS_API_KEY = config.ELEVENLABS_API_KEY
VOICE_ID = config.VOICE_ID

def generate_chat_response(user_input):

    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")  
        response = model.generate_content(user_input)  
        return response.text  # ✅ Extract text response

    except Exception as e:
        return f"Error: {str(e)}"


def generate_speech(text):
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.7}
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content  # Returns audio binary data
    else:
        return None

@app.route("/")
def home():
    
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    
    user_message = request.json.get("message", "")
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    bot_response = generate_chat_response(user_message)
    audio_data = generate_speech(bot_response)

    if audio_data:
        return jsonify({"response": bot_response, "audio": audio_data.hex()})
    else:
        return jsonify({"response": bot_response, "error": "Speech synthesis failed"})

if __name__ == "__main__":
    app.run(debug=True)
