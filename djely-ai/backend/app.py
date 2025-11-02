# backend/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import datetime
import os

app = Flask(__name__)
CORS(app)

# === SYSTÈME DE TICKETS SIMPLE ===
class TicketSystem:
    def __init__(self):
        self.filename = "tickets.json"
        self.load_tickets()
    
    def load_tickets(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {"tickets": [], "next_id": 1}
    
    def save_tickets(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def create_ticket(self, user_id, problem_type, location):
        ticket = {
            "id": self.data["next_id"],
            "user_id": user_id,
            "type": problem_type,
            "location": location,
            "status": "nouveau",
            "created_at": datetime.datetime.now().isoformat()
        }
        
        self.data["tickets"].append(ticket)
        self.data["next_id"] += 1
        self.save_tickets()
        return ticket["id"]
    
    def get_tickets(self):
        return self.data["tickets"]

# Initialisation
ticket_system = TicketSystem()

# === ROUTES PRINCIPALES ===
@app.route('/')
def home():
    return "🚀 Djely AI Backend is Running!"

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """Endpoint pour le chat"""
    user_data = request.json
    user_message = user_data.get('message', '').lower()
    user_id = user_data.get('user_id', 'web_user')
    
    # LOGIQUE CONVERSATIONNELLE SIMPLE
    if "panne" in user_message:
        response = "Je note votre panne. Dans quel quartier ou commune êtes-vous situé ?"
    
    elif "facture" in user_message:
        response = "Je peux vous aider avec votre facture. Quel est le problème ?"
    
    elif "bonjour" in user_message or "salut" in user_message:
        response = "👋 Bonjour ! Je suis Djely AI. Je peux vous aider avec : pannes, factures, urgences. Dites-moi comment vous aider !"
    
    else:
        response = "Je suis Djely, assistant SOG. Dites 'panne', 'facture' ou 'urgence' pour commencer."
    
    return jsonify({"reply": response, "status": "success"})

@app.route('/api/tickets', methods=['GET'])
def get_all_tickets():
    """Endpoint pour récupérer tous les tickets"""
    return jsonify(ticket_system.get_tickets())

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Endpoint pour les statistiques"""
    tickets = ticket_system.get_tickets()
    stats = {
        "total": len(tickets),
        "nouveaux": len([t for t in tickets if t['status'] == 'nouveau']),
        "message": "Système opérationnel"
    }
    return jsonify(stats)

if __name__ == '__main__':
    print("🚀 Démarrage de Djely AI...")
    print("📡 Accessible sur: http://localhost:5000")
    app.run(debug=True, port=5000)