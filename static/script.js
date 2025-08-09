// script.js

// Referenzen zu den HTML-Elementen, die wir oft brauchen
const spielbrettContainer = document.getElementById('spielbrett-container');
const statusText = document.getElementById('status-text');
const neustartButton = document.getElementById('neustart-button');

/**
 * Zeichnet das gesamte Spielbrett und fügt Klick-Events hinzu.
 * @param {object} spielDaten - Das vom Server gesendete JSON-Objekt.
 */
function zeichneSpielbrett(spielDaten) {
    const gridContainer = document.getElementById('spielbrett-grid');
    gridContainer.innerHTML = ''; // Altes Brett leeren

    // 1. Kalaha von Spieler 2 (links) erstellen
    const kalaha2 = document.createElement('div');
    kalaha2.id = 'kalaha-spieler2';
    kalaha2.className = 'kalaha';
    kalaha2.innerText = spielDaten.mulden[13];
    gridContainer.appendChild(kalaha2);

    // 2. Kalaha von Spieler 1 (rechts) erstellen
    const kalaha1 = document.createElement('div');
    kalaha1.id = 'kalaha-spieler1';
    kalaha1.className = 'kalaha';
    kalaha1.innerText = spielDaten.mulden[6];
    gridContainer.appendChild(kalaha1);

    // 3. Spielmulden erstellen
    // Mulden für Spieler 1 (unten, Index 0-5)
    for (let i = 0; i <= 5; i++) {
        const mulde = document.createElement('div');
        mulde.className = 'mulde';
        mulde.dataset.index = i;
        mulde.dataset.spieler = '1';
        mulde.innerText = spielDaten.mulden[i];

        if (spielDaten.aktueller_spieler === 1 && spielDaten.mulden[i] > 0 && !spielDaten.spiel_beendet) {
            mulde.classList.add('clickable');
            mulde.addEventListener('click', async () => {
                if (document.body.classList.contains('warten')) return;
                document.body.classList.add('warten');
                statusText.innerText = 'KI überlegt...';
                await fetch('/api/mache_zug/' + i);
                await updateSpiel();
                document.body.classList.remove('warten');
            });
        }
        gridContainer.appendChild(mulde);
    }

    // Mulden für Spieler 2 (oben, Index 7-12)
    // Wir iterieren RÜCKWÄRTS von 12 nach 7, um die visuelle Reihenfolge korrekt zu halten!
    for (let i = 12; i >= 7; i--) {
        const mulde = document.createElement('div');
        mulde.className = 'mulde';
        mulde.dataset.index = i;
        mulde.dataset.spieler = '2';
        mulde.innerText = spielDaten.mulden[i];
        gridContainer.appendChild(mulde);
    }
    
    // 4. Spiel-Status aktualisieren
    const statusText = document.getElementById('status-text');
    if (spielDaten.spiel_beendet) {
        if(spielDaten.gewinner === 1) statusText.innerText = 'Glückwunsch, Sie haben gewonnen!';
        else if(spielDaten.gewinner === 2) statusText.innerText = 'Die KI hat gewonnen.';
        else statusText.innerText = 'Unentschieden!';
    } else {
        statusText.innerText = `Spieler ${spielDaten.aktueller_spieler} ist am Zug.`;
    }
}

// in static/script.js

function zeichneVerlauf(verlaufDaten) {
    const verlaufListe = document.getElementById('verlauf-liste');

    // NEU: Sicherheitsprüfung. Falls das Element nicht gefunden wird,
    // geben wir eine klare Fehlermeldung aus und brechen ab.
    if (!verlaufListe) {
        console.error("FATALER FEHLER: Das HTML-Element mit der ID 'verlauf-liste' wurde nicht gefunden!");
        return;
    }

    verlaufListe.innerHTML = ''; // Alte Liste leeren

    // Wir zeigen die Liste in umgekehrter Reihenfolge an (neuester Zug oben)
    verlaufDaten.reverse().forEach(eintrag => {
        const p = document.createElement('p');
        p.textContent = eintrag;
        verlaufListe.appendChild(p);
    });
}

/**
 * Die Hauptfunktion, die den Spielzustand vom Server holt und die Seite aktualisiert.
 */
async function updateSpiel() {
    try {
        // NEU: Wir holen Spielstand und Verlauf gleichzeitig
        const [spielResponse, verlaufResponse] = await Promise.all([
            fetch('/api/spielstand'),
            fetch('/api/verlauf')
        ]);

        if (!spielResponse.ok || !verlaufResponse.ok) {
            throw new Error(`HTTP error!`);
        }
        
        const spielDaten = await spielResponse.json();
        const verlaufDaten = await verlaufResponse.json();
        
        // Beide Teile der Seite neu zeichnen
        zeichneSpielbrett(spielDaten);
        zeichneVerlauf(verlaufDaten);

    } catch (error) {
        console.error("Fehler beim Abrufen der Daten:", error);
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