const backendUrl = 'http://localhost:5000';

// Pour charger les données du dashboard
async function loadDashboard() {
    try {
        // Pour charger les statistiques
        const statsResponse = await fetch(`${backendUrl}/api/dashboard/stats`);
        const stats = await statsResponse.json();
        
        // Pour mettre à jour l'interface
        document.getElementById('totalTickets').textContent = stats.total_tickets;
        document.getElementById('newTickets').textContent = stats.tickets_nouveaux;
        document.getElementById('urgentTickets').textContent = stats.urgent_tickets;
        document.getElementById('resolvedTickets').textContent = stats.tickets_resolus;
        
        // Pour charger les tickets
        const ticketsResponse = await fetch(`${backendUrl}/api/tickets`);
        const tickets = await ticketsResponse.json();
        displayTickets(tickets.slice(-10).reverse()); // Les 10 plus récents
        
        // Pour afficher les localisations
        displayLocations(stats.localisations_top);
        
    } catch (error) {
        console.error('Erreur chargement dashboard:', error);
    }
}

// Pour afficher la liste des tickets
function displayTickets(tickets) {
    const ticketsList = document.getElementById('ticketsList');
    
    if (tickets.length === 0) {
        ticketsList.innerHTML = '<div class="ticket-item">Aucun ticket pour le moment</div>';
        return;
    }
    
    ticketsList.innerHTML = tickets.map(ticket => `
        <div class="ticket-item ${getTicketClass(ticket)}">
            <div>
                <strong>Ticket #${ticket.id}</strong> - ${ticket.location || 'Non spécifié'}
                <br>
                <small>Type: ${ticket.type} | ${formatDate(ticket.created_at)}</small>
            </div>
            <span class="badge ${getBadgeClass(ticket)}">${ticket.status}</span>
        </div>
    `).join('');
}

// Pour afficher les localisations
function displayLocations(locations) {
    const locationsMap = document.getElementById('locationsMap');
    
    locationsMap.innerHTML = locations.map(loc => `
        <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px;">
            📍 <strong>${loc.location}</strong> - ${loc.count} ticket(s)
        </div>
    `).join('');
}

// Classes CSS pour les tickets
function getTicketClass(ticket) {
    if (ticket.type === 'urgence_medicale') return 'ticket-urgent';
    if (ticket.status === 'nouveau') return 'ticket-new';
    if (ticket.status === 'resolu') return 'ticket-resolved';
    return '';
}

function getBadgeClass(ticket) {
    if (ticket.type === 'urgence_medicale') return 'badge-urgent';
    if (ticket.status === 'nouveau') return 'badge-new';
    if (ticket.status === 'resolu') return 'badge-resolved';
    return 'badge-new';
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString('fr-FR');
}

// Actualiser toutes les 30 secondes
setInterval(loadDashboard, 30000);
loadDashboard(); // Chargement initial