// script.js

// Referenzen zu den HTML-Elementen, die wir oft brauchen
const spielbrettContainer = document.getElementById('spielbrett-container');
const statusText = document.getElementById('status-text');
const neustartButton = document.getElementById('neustart-button');

/**
 * Zeichnet das gesamte Spielbrett basierend auf den Daten vom Server.
 * @param {object} spielDaten - Das vom Server gesendete JSON-Objekt.
 */
function zeichneSpielbrett(spielDaten) {
    // 1. Altes Brett leeren, bevor wir neu zeichnen
    spielbrettContainer.innerHTML = '';

    // Wir erstellen einen Container für die Mulden von Spieler 2 (oben)
    const spieler2Reihe = document.createElement('div');
    spieler2Reihe.classList.add('mulden-reihe');

    // Wir erstellen einen Container für die Mulden von Spieler 1 (unten)
    const spieler1Reihe = document.createElement('div');
    spieler1Reihe.classList.add('mulden-reihe');

    // 2. Durch die Mulden-Liste iterieren und für jede Mulde ein Element erstellen
    spielDaten.mulden.forEach((anzahlSteine, index) => {
        const mulde = document.createElement('div');
        mulde.innerText = anzahlSteine; // Die Anzahl der Steine anzeigen
        mulde.dataset.index = index;    // Den Index als data-Attribut speichern

        if (index === 6 || index === 13) {
            // Das sind die Kalahas (Gewinnmulden)
            mulde.classList.add('kalaha');
            if (index === 6) {
                mulde.id = 'kalaha-spieler1';
            } else {
                mulde.id = 'kalaha-spieler2';
            }
        } else {
            // Das sind die normalen Spielmulden
            mulde.classList.add('mulde');
            // Hier könnten wir später Klick-Events hinzufügen
        }
        
        // Die Mulden den richtigen Reihen zuordnen
        if (index >= 0 && index <= 5) {
            spieler1Reihe.appendChild(mulde);
        } else if (index >= 7 && index <= 12) {
            // Wir fügen die oberen Mulden in umgekehrter Reihenfolge ein,
            // damit sie von rechts nach links angezeigt werden.
            spieler2Reihe.prepend(mulde);
        }
    });

    // Die fertigen Reihen und die Kalahas in der richtigen Reihenfolge ins Haupt-div einfügen
    spielbrettContainer.appendChild(document.getElementById('kalaha-spieler2'));
    spielbrettContainer.appendChild(spieler2Reihe);
    spielbrettContainer.appendChild(document.getElementById('kalaha-spieler1'));
    spielbrettContainer.appendChild(spieler1Reihe);


    // 3. Spiel-Status aktualisieren
    if (spielDaten.spiel_beendet) {
        statusText.innerText = `Spiel beendet! Gewinner: Spieler ${spielDaten.gewinner}`;
    } else {
        statusText.innerText = `Spieler ${spielDaten.aktueller_spieler} ist am Zug.`;
    }
}


/**
 * Die Hauptfunktion, die den Spielzustand vom Server holt und die Seite aktualisiert.
 */
async function updateSpiel() {
    try {
        const response = await fetch('/api/spielstand'); // 1. Daten anfordern
        if (!response.ok) { // Fehlerbehandlung, falls Server einen Fehler meldet
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const spielDaten = await response.json(); // 2. Daten als JSON auspacken
        zeichneSpielbrett(spielDaten); // 3. Brett mit den neuen Daten zeichnen
    } catch (error) {
        console.error("Fehler beim Abrufen der Spieldaten:", error);
        statusText.innerText = "Fehler bei der Verbindung zum Server.";
    }
}

// Event-Listener für den Neustart-Button
neustartButton.addEventListener('click', async () => {
    await fetch('/api/neues_spiel');
    updateSpiel();
});


// Das Spiel zum ersten Mal laden, wenn die Seite aufgerufen wird.
updateSpiel();