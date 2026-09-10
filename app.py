"""
app.py
Flask backend for PlantCareBot AI chatbot.
Uses Google Gemini API (gemini-3.1-flash-lite) for text + image based chat,
scoped only to plant care / gardening topics via chatbot_config.py.
"""

import os
import base64
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-3.1-flash-lite",
    system_instruction=SYSTEM_PROMPT,
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.form.get("message", "").strip()
        image_file = request.files.get("image")

        content_parts = []

        if user_message:
            content_parts.append(user_message)

        if image_file:
            image_bytes = image_file.read()
            content_parts.append(
                {
                    "mime_type": image_file.mimetype,
                    "data": base64.b64encode(image_bytes).decode("utf-8"),
                }
            )

        if not content_parts:
            return jsonify({"reply": "Please type a message or attach an image."}), 400

        response = model.generate_content(content_parts)
        reply_text = response.text if response.text else "Sorry, I couldn't generate a response."

        return jsonify({"reply": reply_text})

    except Exception as e:
        return jsonify({"reply": f"Something went wrong: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
