from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import datetime
import os

app = Flask(__name__)
CORS(app)

# Les 2 Systemes De Gestion
class ConversationManager:
    def __init__(self):
        self.user_states = {}  # {user_id: "state", ...}
    
    def get_state(self, user_id):
        return self.user_states.get(user_id, "idle")
    
    def set_state(self, user_id, state, data=None):
        self.user_states[user_id] = {"state": state, "data": data or {}}
    
    def clear_state(self, user_id):
        if user_id in self.user_states:
            del self.user_states[user_id]
    
    def get_data(self, user_id, key=None):
        if user_id in self.user_states and self.user_states[user_id].get("data"):
            if key:
                return self.user_states[user_id]["data"].get(key)
            return self.user_states[user_id]["data"]
        return None
    
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
conv_manager = ConversationManager()

# Les Routes Principales
@app.route('/')
def home():
    return "🚀 Djely AI Backend Est En Cours!"

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    user_data = request.json
    user_message = user_data.get('message', '').lower()
    user_id = user_data.get('user_id', 'anonymous')
    
    current_state = conv_manager.get_state(user_id)
    
    # La Logique Par Situation Ou Etat
    if current_state == "awaiting_location":
        return handle_location_response(user_id, user_message)
    
    elif current_state == "awaiting_bill_detail":
        return handle_bill_response(user_id, user_message)
    
    elif current_state == "awaiting_emergency_location":
        return handle_emergency_response(user_id, user_message)
    
    # Sinon Nouvelle Conversation
    else:
        return handle_new_conversation(user_id, user_message)

def handle_new_conversation(user_id, message):
    # Gère le début d'une conversation
    if "panne" in message or "coupure" in message or "blackout" in message:
        conv_manager.set_state(user_id, "awaiting_location")
        response = "🔧 Je note votre panne. Dans quel quartier ou commune êtes-vous situé ?"
    
    elif "facture" in message or "invoice" in message or "payer" in message:
        conv_manager.set_state(user_id, "awaiting_bill_detail")
        response = "📊 Je peux vous aider avec votre facture. Quel est le problème précis ?\n• Montant trop élevé\n• Comprendre la consommation\n• Délai de paiement\n• Erreur sur la facture"
    
    elif "urgence" in message or "médical" in message or "hôpital" in message or "clinique" in message:
        conv_manager.set_state(user_id, "awaiting_emergency_location")
        response = "🚨 URGENCE MÉDICALE DÉTECTÉE ! Quel est le nom et l'adresse de l'établissement de santé ?"
    
    elif "bonjour" in message or "salut" in message or "hello" in message:
        response = "👋 Bonjour ! Je suis Djely AI, votre assistant EDG. Je peux vous aider avec :\n• 🚨 Signalement de pannes\n• 📊 Questions sur les factures\n• 💊 Urgences médicales\n• ℹ️ Informations service client\n\nDites-moi comment puis-vous assister !"
    
    elif "merci" in message or "bye" in message or "au revoir" in message:
        response = "👍 Je vous remercie ! N'hésitez pas si vous avez d'autres questions. Bonne journée !"
        conv_manager.clear_state(user_id)
    
    else:
        response = "🤔 Je n'ai pas bien compris. Je peux vous aider avec :\n• 🚨 Pannes d'électricité\n• 📊 Factures et paiements\n• 💊 Situations d'urgence\n• ℹ️ Informations générales\n\nDites 'panne', 'facture' ou 'urgence' pour commencer."
    
    return jsonify({"reply": response, "status": "success"})

def handle_location_response(user_id, location):
    # Gère la réponse de localisation pour une panne
    if location and len(location) > 2:
        # On cree le ticket
        ticket_id = ticket_system.create_ticket(user_id, "panne", location)
        
        # Reponse avec confirmation
        response = f"""✅ **Ticket #{ticket_id} CRÉÉ AVEC SUCCÈS !**

📍 Localisation : {location}
🛠️ Intervention : Technicien alerté
⏱️ Délai estimé : 2-4 heures
📞 Suivi : Vous recevrez des updates

*Merci pour votre signalement !*"""
        
        conv_manager.clear_state(user_id)
        return jsonify({"reply": response, "status": "success", "ticket_id": ticket_id})
    
    else:
        response = "❌ Localisation trop courte. Veuillez préciser votre **quartier, commune ou rue** :"
        return jsonify({"reply": response, "status": "retry"})

def handle_emergency_response(user_id, location):
    # Gère les urgences médicales
    if location and len(location) > 5:
        ticket_id = ticket_system.create_ticket(user_id, "urgence_medicale", location)
        
        response = f"""🚨 **URGENCE MÉDICALE - INTERVENTION IMMÉDIATE !**

🏥 Établissement : {location}
🔴 Priorité : MAXIMUM
⚡ Équipe : Techniciens d'urgence alertés
📞 Contact : Coordinateur urgentiste assigné

**Ticket #{ticket_id} - Intervention en cours**"""
        
        conv_manager.clear_state(user_id)
        return jsonify({"reply": response, "status": "success", "ticket_id": ticket_id, "priority": "urgent"})
    
    else:
        response = "🚨 Veuillez fournir le **nom complet et l'adresse exacte** de l'établissement médical :"
        return jsonify({"reply": response, "status": "retry"})

def handle_bill_response(user_id, bill_detail):
    # Gère les questions de facturation
    responses = {
        "montant": "💡 Pour comprendre votre facture :\n• Vérifiez votre consommation du mois\n• Comparez avec vos appareils utilisés\n• Contactez le service client pour un détail ligne par ligne",
        "consommation": "📈 Votre consommation dépend de :\n• Nombre d'appareils électriques\n• Heures d'utilisation\n• Puissance des équipements\n• Ancienneté des appareils",
        "délai": "⏰ Délais de paiement :\n• Facture payable sous 15 jours\n• Paiement en ligne disponible\n• Retard possible avec pénalité de 5%",
        "erreur": "❌ En cas d'erreur sur la facture :\n• Contactez le service client au 3040\n• Préparez votre numéro de client\n• Ayez la facture concernée sous la main"
    }
    
    response = "Je n'ai pas identifié le problème spécifique. "
    for key, answer in responses.items():
        if key in bill_detail:
            response = answer
            break
    else:
        response += "Dites : 'montant', 'consommation', 'délai' ou 'erreur'"
    
    conv_manager.clear_state(user_id)
    return jsonify({"reply": response, "status": "success"})

@app.route('/api/tickets', methods=['GET'])
def get_all_tickets():
    # Endpoint pour récupérer tous les tickets
    return jsonify(ticket_system.get_tickets())

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # Endpoint pour les statistiques
    tickets = ticket_system.get_tickets()
    stats = {
        "total": len(tickets),
        "nouveaux": len([t for t in tickets if t['status'] == 'nouveau']),
        "message": "Système opérationnel"
    }
    return jsonify(stats)

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    # Statistiques complètes pour le dashboard(tableau de bord)
    tickets = ticket_system.get_tickets()
    
    # Statistiques détaillées
    stats = {
        "total_tickets": len(tickets),
        "tickets_nouveaux": len([t for t in tickets if t['status'] == 'nouveau']),
        "tickets_encours": len([t for t in tickets if t['status'] == 'en_cours']),
        "tickets_resolus": len([t for t in tickets if t['status'] == 'resolu']),
        "urgent_tickets": len([t for t in tickets if "urgence" in t.get('type', '')]),
        
        "types_tickets": {
            "pannes": len([t for t in tickets if t['type'] == 'panne']),
            "urgences_medicales": len([t for t in tickets if t['type'] == 'urgence_medicale']),
            "factures": len([t for t in tickets if "facture" in t.get('type', '')]),
        },
        
        "localisations_top": get_top_locations(tickets),
        "activite_7j": get_weekly_activity(tickets),
        
        "message": f"📊 {len(tickets)} tickets traités aujourd'hui"
    }
    
    return jsonify(stats)

def get_top_locations(tickets, limit=5):
    # Retourne les localisations les plus fréquentes
    locations = {}
    for ticket in tickets:
        loc = ticket.get('location', 'Inconnu')
        locations[loc] = locations.get(loc, 0) + 1
    
    # Trier et limiter
    sorted_locs = sorted(locations.items(), key=lambda x: x[1], reverse=True)
    return [{"location": loc, "count": count} for loc, count in sorted_locs[:limit]]

def get_weekly_activity(tickets):
    # Simule l'activité de la semaine
    from datetime import datetime, timedelta
    
    activity = {}
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        activity[date] = len([t for t in tickets if date in t.get('created_at', '')])
    
    return activity

@app.route('/api/tickets/<int:ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id):
    # Mettre à jour le statut d'un ticket
    data = request.json
    new_status = data.get('status')
    
    tickets = ticket_system.get_tickets()
    for ticket in tickets:
        if ticket['id'] == ticket_id:
            ticket['status'] = new_status
            ticket_system.save_tickets()
            return jsonify({"status": "success", "message": f"Ticket #{ticket_id} mis à jour"})
    
    return jsonify({"status": "error", "message": "Ticket non trouvé"}), 404

if __name__ == '__main__':
    print("🚀 Démarrage de Djely AI...")
    print("📡 Accessible sur: http://localhost:5000")
    app.run(debug=True, port=5000)