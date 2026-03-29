import os
import json
import sqlite3
from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from flask_cors import CORS
import requests

app = Flask(__name__, template_folder='.', static_url_path='', static_folder='.')
CORS(app)

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clients.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            hours TEXT,
            address TEXT,
            faq TEXT,
            is_temp INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def detect_category(description):
    if not description:
        return "generique"
    desc = str(description).lower()
    if any(x in desc for x in ["restaurant", "gastronomie", "cuisine", "bistrot", "manger", "plat", "dejeuner", "diner", "carte", "menu"]):
        return "restaurant"
    if any(x in desc for x in ["boulangerie", "pain", "viennoiserie", "patisserie", "patissier", "croissant", "baguette", "fournil"]):
        return "boulangerie"
    if any(x in desc for x in ["coiffeur", "coiffure", "barbier", "coupe", "cheveux", "salon de coiffure", "visagiste"]):
        return "coiffeur"
    if any(x in desc for x in ["esthetique", "institut", "beaute", "onglerie", "massage", "soin", "visage", "spa", "ongle", "manucure"]):
        return "esthetique"
    if any(x in desc for x in ["garage", "voiture", "mécanique", "réparation", "auto", "pneu", "vidange"]):
        return "garage"
    return "generique"

def get_welcome_message(category, name):
    name_str = name if name else "l'entreprise"
    welcomes = {
        "restaurant": f"Bienvenue chez {name_str} ! Je suis votre assistant pour découvrir notre carte et réserver votre table. Que puis-je pour vous ?",
        "boulangerie": f"Bienvenue chez {name_str} ! Nos pains et viennoiseries sont prêts. Je suis là pour vous conseiller. Quel délice cherchez-vous ?",
        "coiffeur": f"Bienvenue chez {name_str} ! Je suis ravi de vous aider à choisir une prestation ou prendre rendez-vous. Comment puis-je vous sublimer ?",
        "esthetique": f"Bienvenue dans votre institut {name_str} ! Je suis votre assistant bien-être. Souhaitez-vous découvrir nos soins ou un moment de détente ?",
        "garage": f"Bienvenue au garage {name_str} ! Je suis là pour vos questions mécaniques ou vos prises de rendez-vous entretien. Quel est votre besoin ?",
        "generique": f"Bonjour et bienvenue chez {name_str} ! Je suis votre assistant virtuel. Comment puis-je vous renseigner aujourd'hui ?"
    }
    return welcomes.get(category, welcomes["generique"])

def get_system_prompt(client_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, description, hours, address, faq FROM clients WHERE id=?", (client_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        name, description, hours, address, faq = row
        category = detect_category(description)
        welcome = get_welcome_message(category, name)
        
        prompt = f"Tu es l'assistant de l'entreprise suivante:\n"
        prompt += f"Nom: {name or 'Non spécifié'}\n"
        prompt += f"Description: {description or 'Non spécifiée'}\n"
        prompt += f"Catégorie: {category}\n"
        prompt += f"Horaires: {hours or 'Non spécifiés'}\n"
        prompt += f"Adresse: {address or 'Non spécifiée'}\n"
        
        if faq:
            try:
                faqs = json.loads(faq)
                if faqs:
                    prompt += "\nFAQ (Questions courantes et réponses):\n"
                    for f in faqs:
                        prompt += f"- Q: {f.get('question','')}\n  R: {f.get('answer','')}\n"
            except:
                pass
                
        prompt += f"\nMessage de bienvenue acté: {welcome}\n"
        prompt += "\nInstructions: Réponds de manière concise, polie et professionnelle en français. Tu ne dois utiliser QUE les informations ci-dessus. Si une question est hors sujet ou si l'information n'est pas listée, explique aimablement que tu ne sais pas et propose au client de contacter directement l'établissement."
        return prompt, welcome
    return "", ""

def check_auth(username, password):
    return username == 'admin' and password == 'pau2026'

def authenticate():
    return Response(
    'Accès refusé. Veuillez vous identifier.', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

@app.route("/")
def public_page():
    return render_template("public.html")

@app.route("/admin")
def admin_page():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    return render_template("admin.html")

@app.route("/demo")
def demo_page():
    return render_template("widget-demo.html")

@app.route("/api/save-prompt", methods=["POST"])
def save_prompt():
    data = request.json
    client_id = data.get("client_id")
    is_temp = int(data.get("is_temp", 0))
    if not client_id:
        return jsonify({"success": False, "message": "ID Client manquant."}), 400
        
    faq_str = json.dumps(data.get('faq', []))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO clients (id, name, description, hours, address, faq, is_temp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            description = excluded.description,
            hours = excluded.hours,
            address = excluded.address,
            faq = excluded.faq,
            is_temp = excluded.is_temp
    ''', (client_id, data.get('name'), data.get('description'), data.get('hours'), data.get('address'), faq_str, is_temp))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Configuration sauvegardée!"})

@app.route("/api/clients", methods=["GET"])
def get_clients_list():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, is_temp, created_at FROM clients ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    
    active = []
    temp = []
    for row in rows:
        client_data = {"id": row[0], "name": row[1] or 'Sans Nom', "date": row[3]}
        if row[2] == 1:
            temp.append(client_data)
        else:
            active.append(client_data)
            
    return jsonify({"active": active, "temp": temp})

@app.route("/api/get-config", methods=["GET"])
def get_config():
    client_id = request.args.get("id")
    if not client_id:
        return jsonify({})
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, description, hours, address, faq FROM clients WHERE id=?", (client_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        name, description, hours, address, faq = row
        try:
            faq_data = json.loads(faq) if faq else []
        except:
            faq_data = []
        return jsonify({
            "name": name,
            "description": description,
            "hours": hours,
            "address": address,
            "faq": faq_data
        })
    return jsonify({})

@app.route("/api/get-client-profile", methods=["GET"])
def get_client_profile():
    client_id = request.args.get("id")
    if not client_id:
        return jsonify({"name": "Démo", "category": "generique", "welcome": "Bonjour !"})
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, description FROM clients WHERE id=?", (client_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        name, description = row
        category = detect_category(description)
        welcome = get_welcome_message(category, name)
        return jsonify({
            "name": name,
            "category": category,
            "welcome": welcome
        })
    return jsonify({"name": "Inconnu", "category": "generique", "welcome": "Bonjour !"})

@app.route("/chat", methods=["POST"])
def chat():
    api_key = "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"
    data = request.json
    client_id = data.get("client_id")
    if not client_id:
        return jsonify({"response": "Erreur: ID client manquant."}), 400
        
    user_message = data.get("message")
    chat_history = data.get("history", [])
    
    system_instruction, welcome_msg = get_system_prompt(client_id)
    if not system_instruction:
        return jsonify({"response": "Erreur: Ce client n'existe pas dans la base."}), 404
    
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

@app.route("/api/delete-client/<client_id>", methods=["DELETE"])
def delete_client(client_id):
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM clients WHERE id=?", (client_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": f"Client {client_id} supprimé."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
