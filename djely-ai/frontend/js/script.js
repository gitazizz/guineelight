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

// Gestion vocale
let isListening = false;
let recognition = null;
let currentLanguage = 'fr';

function toggleVoice() {
    const selector = document.getElementById('languageSelector');
    selector.style.display = selector.style.display === 'none' ? 'block' : 'none';
    
    if (!isListening) {
        startVoiceRecognition();
    } else {
        stopVoiceRecognition();
    }
}

function changeLanguage() {
    currentLanguage = document.getElementById('languageSelect').value;
    document.getElementById('voiceStatus').textContent = getLanguageMessage('ready');
}

function getLanguageMessage(key) {
    const messages = {
        fr: {
            ready: "Cliquez 🎤 pour parler",
            listening: "🎤 Écoute en cours...",
            processing: "Traitement en cours...",
            error: "Erreur de reconnaissance vocale"
        },
        bambara: {
            ready: "I n'a fɔ 🎤 ka kuma",
            listening: "🎤 M bɛ kalan...", 
            processing: "Baarakɛcogo bɛ kɛ...",
            error: "Kuma dɔnni jugu"
        }
    };
    return (messages[currentLanguage] || messages.fr)[key];
}

function startVoiceRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert("Reconnaissance vocale non supportée sur ce navigateur");
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = getLanguageCode(currentLanguage);
    
    recognition.onstart = function() {
        isListening = true;
        document.getElementById('voiceStatus').textContent = getLanguageMessage('listening');
        document.getElementById('voiceButton').style.background = '#dc3545';
    };
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('voiceStatus').textContent = getLanguageMessage('processing');
        
        // Envoyer au backend pour traitement
        processVoiceCommand(transcript);
    };
    
    recognition.onerror = function(event) {
        console.error('Erreur reconnaissance:', event.error);
        document.getElementById('voiceStatus').textContent = getLanguageMessage('error');
        stopVoiceRecognition();
    };
    
    recognition.onend = function() {
        stopVoiceRecognition();
    };
    
    recognition.start();
}

function stopVoiceRecognition() {
    if (recognition) {
        recognition.stop();
    }
    isListening = false;
    document.getElementById('voiceButton').style.background = '#28a745';
    document.getElementById('voiceStatus').textContent = getLanguageMessage('ready');
}

function getLanguageCode(lang) {
    const codes = {
        'fr': 'fr-FR',
        'bambara': 'fr-FR', // Utiliser français comme base
        'pular': 'fr-FR', 
        'susu': 'fr-FR'
    };
    return codes[lang] || 'fr-FR';
}

async function processVoiceCommand(voiceText) {
    try {
        const response = await fetch(`${backendUrl}/api/voice/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: voiceText,
                language: currentLanguage,
                user_id: 'voice_user_' + Date.now()
            })
        });
        
        const data = await response.json();
        
        // Afficher la réponse dans le chat
        const messageToDisplay = currentLanguage === 'fr' ? data.message_fr : data.message_local;
        displayMessage(`🎤 ${voiceText}`, 'user');
        displayMessage(messageToDisplay, 'bot');
        
        // Si besoin d'étape suivante, préparer l'input
        if (data.next_step && data.next_step !== 'retry') {
            document.getElementById('userInput').placeholder = "Répondez ici...";
            document.getElementById('userInput').focus();
        }
        
    } catch (error) {
        console.error('Erreur traitement vocal:', error);
        displayMessage('❌ Erreur de traitement vocal', 'bot');
    }
    
    stopVoiceRecognition();
}