import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from flask_cors import CORS
import requests

app = Flask(__name__, template_folder='.', static_url_path='', static_folder='.')
CORS(app)

PROMPT_FILE = "prompt_data.json"

def get_system_prompt():
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            prompt = f"Tu es l'assistant de l'entreprise suivante:\n"
            prompt += f"Nom: {data.get('name', '')}\n"
            prompt += f"Description: {data.get('description', '')}\n"
            prompt += f"Horaires: {data.get('hours', '')}\n"
            prompt += f"Adresse: {data.get('address', '')}\n"
            
            faqs = data.get('faq', [])
            if faqs:
                prompt += "\nFAQ (Questions courantes et réponses):\n"
                for faq in faqs:
                    prompt += f"- Q: {faq.get('question','')}\n  R: {faq.get('answer','')}\n"
                    
            prompt += "\nInstructions: Réponds de manière concise, polie et professionnelle en français. Tu ne dois utiliser QUE les informations ci-dessus. Si une question est hors sujet ou si l'information n'est pas listée, explique aimablement que tu ne sais pas et propose au client de contacter directement l'établissement."
            return prompt
    return "Tu es un assistant IA. Aucune configuration n'a été trouvée, demande au propriétaire de configurer l'interface d'administration."

def check_auth(username, password):
    return username == 'admin' and password == 'pau2026'

def authenticate():
    return Response(
    'Accès refusé. Veuillez vous identifier.', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route("/")
def admin_page():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
        
    if os.path.exists(PROMPT_FILE):
        try:
            os.remove(PROMPT_FILE)
        except Exception:
            pass
            
    return render_template("index.html")

@app.route("/demo")
def demo_page():
    return render_template("widget-demo.html")

@app.route("/api/save-prompt", methods=["POST"])
def save_prompt():
    data = request.json
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return jsonify({"success": True, "message": "Configuration sauvegardée avec succès et instructions système mises à jour."})

@app.route("/api/get-config", methods=["GET"])
def get_config():
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({})

@app.route("/chat", methods=["POST"])
def chat():
    api_key = "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"
    data = request.json
    user_message = data.get("message")
    chat_history = data.get("history", [])
    system_instruction = get_system_prompt()
    
    messages = [{"role": "system", "content": system_instruction}]
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "assistant"
        messages.append({"role": role, "content": msg["message"]})
    messages.append({"role": "user", "content": user_message})
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "max_tokens": 500
        }
    )
    result = response.json()
    return jsonify({"response": result["choices"][0]["message"]["content"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
