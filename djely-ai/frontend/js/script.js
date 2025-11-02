const backendUrl = 'http://localhost:5000';
        
// Fonction pour envoyer un message
async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Afficher le message de l'utilisateur
    displayMessage(message, 'user');
    userInput.value = '';
    
    try {
        // Envoyer au backend
        const response = await fetch(`${backendUrl}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: 'web_user_' + Date.now()
            })
        });
        
        const data = await response.json();
        displayMessage(data.reply, 'bot');
        
    } catch (error) {
        console.error('Erreur:', error);
        displayMessage('⚠️ Service temporairement indisponible. Veuillez réessayer.', 'bot');
    }
}

// Fonction pour les boutons rapides
function quickMessage(text) {
    document.getElementById('userInput').value = text;
    sendMessage();
}

// Affichage des messages
function displayMessage(text, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Appuyer sur Entrée pour envoyer
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Focus automatique sur l'input
document.getElementById('userInput').focus();