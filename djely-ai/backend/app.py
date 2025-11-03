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
    
    def create_ticket_with_notification(user_id, problem_type, location):
        ticket_id = ticket_system.create_ticket(user_id, problem_type, location)
        
        # Ajouter notification
        if problem_type == "urgence_medicale":
            notification_system.add_notification(
                "🚨 URGENCE MÉDICALE",
                f"Ticket #{ticket_id} - {location}",
                "urgent"
            )
        else:
            notification_system.add_notification(
                "🆕 Nouveau Ticket",
                f"Ticket #{ticket_id} - {location}",
                "info"
            )
        
        return ticket_id

# Notifications Et Alertes
class NotificationSystem:
    def __init__(self):
        self.notifications = []
    
    def add_notification(self, title, message, level="info"):
        notification = {
            "id": len(self.notifications) + 1,
            "title": title,
            "message": message, 
            "level": level,  # info, warning, urgent
            "timestamp": datetime.datetime.now().isoformat(),
            "read": False
        }
        self.notifications.append(notification)
        return notification
    
# Initialisation
ticket_system = TicketSystem()
conv_manager = ConversationManager()
notification_system = NotificationSystem()

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
        ticket_id = ticket_system.create_ticket_with_notification(user_id, "panne", location)
        
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
        ticket_id = ticket_system.create_ticket_with_notification(user_id, "urgence_medicale", location)
        
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

# Support Vocal Multilangue
@app.route('/api/voice/process', methods=['POST'])
def process_voice_command():
    # Endpoint pour traiter les commandes vocales
    data = request.json
    voice_text = data.get('text', '').lower()
    language = data.get('language', 'fr')
    user_id = data.get('user_id', 'anonymous')
    
    # Détection de langue basique
    if any(word in voice_text for word in ['panne', 'coupure', 'électricité']):
        response = {
            "type": "panne_detected",
            "message_fr": "Je détecte une panne. Quel est votre quartier ?",
            "message_local": "N yɛlɛma dɔnnen don. I bɛ dugu jumen ?",
            "next_step": "location"
        }
    
    elif any(word in voice_text for word in ['facture', 'payer', 'argent']):
        response = {
            "type": "facture_detected", 
            "message_fr": "Je comprends une question de facture. Quel est le problème ?",
            "message_local": "N yɛ ka sɔrɔ wariko la. Mun na ?",
            "next_step": "facture_detail"
        }
    
    elif any(word in voice_text for word in ['urgence', 'hôpital', 'médecin']):
        response = {
            "type": "urgence_detected",
            "message_fr": "🚨 URGENCE DÉTECTÉE ! Quel établissement médical ?",
            "message_local": "🚨 Dɛsɛ dɔnnen ! Dɔgɔtɔrɔso jumen ?",
            "next_step": "urgence_location"
        }
    
    else:
        response = {
            "type": "not_understood",
            "message_fr": "Je n'ai pas compris. Dites 'panne', 'facture' ou 'urgence'",
            "message_local": "N ma kà sira. Fɔ 'panne', 'facture' walima 'urgence'",
            "next_step": "retry"
        }
    
    return jsonify(response)

# Dictionnaire de phrases locales
PHRASES_LOCALES = {
    "fr": {
        "welcome": "Bonjour, je suis Djely AI. Comment puis-vous aider ?",
        "panne_ask_location": "Quel est votre quartier ou commune ?",
        "urgence_ask_location": "Quel établissement médical ?",
        "confirmation": "Merci, ticket créé avec succès"
    },
    "bambara": {
        "welcome": "I ni ce, ne ye Djely AI ye. I bɛ se ka n dɛmɛ ?",
        "panne_ask_location": "I bɛ dugu jumen ?", 
        "urgence_ask_location": "Dɔgɔtɔrɔso jumen ?",
        "confirmation": "A ni ce, ticket labɛn don"
    }
}

@app.route('/api/languages', methods=['GET'])
def get_supported_languages():
    # Retourne les langues supportées
    return jsonify({
        "languages": [
            {"code": "fr", "name": "Français", "native": "Français"},
            {"code": "bambara", "name": "Bambara", "native": "Bamanankan"},
            {"code": "pular", "name": "Peul", "native": "Pular"},
            {"code": "susu", "name": "Soussou", "native": "Sosoxui"}
        ]
    })
    
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    # Récupérer les notifications
    return jsonify({
        "notifications": notification_system.notifications[-10:][::-1],  # 10 plus récentes
        "unread_count": len([n for n in notification_system.notifications if not n['read']])
    })

@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    # Marquer une notification comme lue
    for notification in notification_system.notifications:
        if notification['id'] == notification_id:
            notification['read'] = True
            return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 404

# Route De Test Pour Ticket
@app.route('/api/test/create-ticket', methods=['GET'])
def test_create_ticket():
    # Test manuel - Créer un ticket directement
    try:
        print("🧪 Test création ticket démarré...")
        
        # Créer un ticket SIMPLE
        ticket_id = ticket_system.create_ticket(
            "test_user", 
            "test_panne", 
            "Test_Location"
        )
        
        if ticket_id:
            return jsonify({
                "success": True,
                "ticket_id": ticket_id,
                "message": f"✅ Ticket #{ticket_id} créé avec succès!",
                "total_tickets": len(ticket_system.get_tickets())
            })
        else:
            return jsonify({
                "success": False,
                "message": "❌ Échec création ticket"
            })
            
    except Exception as e:
        print(f"💥 Erreur test: {e}")
        return jsonify({
            "success": False,
            "message": f"❌ Erreur: {str(e)}"
        })
        
@app.route('/api/test/hello', methods=['GET'])
def test_hello():
    # Test simple pour vérifier que le serveur marche
    return jsonify({
        "message": "🚀 Serveur Djely AI fonctionnel!",
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat()
    })
    
    
if __name__ == '__main__':
    print("🚀 Démarrage de Djely AI...")
    print("📡 Accessible sur: http://localhost:5000")
    app.run(debug=True, port=5000)