import functions_framework
import google.generativeai as genai
import os
from flask import jsonify, Request
import requests
from typing import Dict, Any

# Configure environment variables
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')


def send_telegram_message(chat_id: int, text: str) -> None:
    """Send message back to Telegram chat"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)


def generate_response(prompt: str) -> str:
    """Generate response using Gemini API"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"


@functions_framework.http
def telegram_webhook(request: Request) -> Dict[str, Any]:
    """Main webhook handler for Telegram messages"""
    if request.method != "POST":
        return jsonify({"error": "Only POST requests are accepted"})

    try:
        # Parse Telegram update
        update = request.get_json()

        # Check if it's a message
        if "message" not in update:
            return jsonify({"status": "not a message"})

        message = update["message"]
        chat_id = message["chat"]["id"]

        # Handle only text messages
        if "text" not in message:
            send_telegram_message(chat_id, "Please send text messages only.")
            return jsonify({"status": "non-text message"})

        user_message = message["text"]

        # Generate response using Gemini
        ai_response = generate_response(user_message)

        # Send response back to user
        send_telegram_message(chat_id, ai_response)

        return jsonify({"status": "success"})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)})