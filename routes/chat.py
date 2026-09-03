# from flask import Blueprint, request, jsonify, current_app
# import requests
# import json

# chat_bp = Blueprint("chat", __name__)

# SYSTEM_PROMPT = """You are PlaceIQ Assistant — a helpful AI embedded in PlaceIQ, a college placement intelligence platform built by Ritesh Kumar Singh (B.Tech student at GLBITM, Greater Noida). Help students with college selection, placement strategy, GATE/CAT prep, and career advice. Be friendly, concise, and helpful."""

# @chat_bp.route("", methods=["POST"])
# def chat():
#     try:
#         data = request.get_json(silent=True) or {}
#         messages = data.get("messages", [])
        
#         # Handle single message format
#         if not messages and data.get("message"):
#             messages = [{"role": "user", "content": data.get("message")}]
        
#         if not messages:
#             return jsonify({"error": "No message provided"}), 400
        
#         # Get API key from config
#         api_key = current_app.config.get("GROQ_API_KEY")
#         if not api_key:
#             return jsonify({"error": "GROQ API key not configured"}), 500
        
#         # Prepare messages with system prompt
#         full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages[-20:]
        
#         # Make request to Groq API
#         headers = {
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json"
#         }
        
#         payload = {
#             "model": "openai/gpt-oss-20b",
#             "messages": full_messages,
#             "max_tokens": 500,
#             "temperature": 0.7
#         }
        
#         response = requests.post(
#             "https://api.groq.com/openai/v1/chat/completions",
#             headers=headers,
#             json=payload,
#             timeout=30
#         )
        
#         if response.status_code != 200:
#             print(f"Groq API error: {response.status_code} - {response.text}")
#             return jsonify({"error": f"API error: {response.status_code}"}), 503
        
#         result = response.json()
#         reply = result["choices"][0]["message"]["content"]
        
#         return jsonify({"reply": reply})
        
#     except requests.exceptions.Timeout:
#         return jsonify({"error": "Request timeout. Please try again."}), 503
#     except Exception as e:
#         print(f"Chat error: {str(e)}")
#         return jsonify({"error": str(e)}), 500                              


from flask import Blueprint, request, jsonify, current_app
import requests

chat_bp = Blueprint("chat", __name__)

SYSTEM_PROMPT = """You are PlaceIQ Assistant — a helpful AI embedded in PlaceIQ, a college placement intelligence platform built by Ritesh Kumar Singh (B.Tech student at GLBITM, Greater Noida). Help students with college selection, placement strategy, GATE/CAT prep, and career advice. Be friendly and concise."""

@chat_bp.route("", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        messages = data.get("messages", [])
        
        if not messages and data.get("message"):
            messages = [{"role": "user", "content": data.get("message")}]
        
        if not messages:
            return jsonify({"error": "No message provided"}), 400
        
        api_key = current_app.config.get("GROQ_API_KEY")
        
        if not api_key:
            return jsonify({"error": "API key not configured"}), 500
        
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages[-20:]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": full_messages,
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            return jsonify({"error": f"API error: {response.status_code}"}), 503
        
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        
        return jsonify({"reply": reply})
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500
