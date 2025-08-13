// script.js

// Referenzen zu den HTML-Elementen, die wir oft brauchen
const spielbrettContainer = document.getElementById('spielbrett-container');
const statusText = document.getElementById('status-text');
const neustartButton = document.getElementById('neustart-button');
const starterAuswahl = document.getElementById('starter-auswahl');
const kiTiefeAuswahl = document.getElementById('ki-tiefe-auswahl');
const kiTiefeWert = document.getElementById('ki-tiefe-wert');

kiTiefeAuswahl.addEventListener('input', () => {
    kiTiefeAuswahl.textContent = kiTiefeAuswahl.value;
});


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
            // Und im `zeichneSpielbrett` EventListener ersetzen:
            // alt: mulde.addEventListener('click', async () => { ... });
            // neu:
            mulde.addEventListener('click', () => animiereZug(i));
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
    const starter = starterAuswahl.value;
    const max_tiefe = kiTiefeAuswahl.value;

    // Wir senden die Daten jetzt als POST-Request mit JSON-Body
    await fetch('/api/neues_spiel', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            starter: starter,
            max_tiefe: max_tiefe
        })
    });
    updateSpiel();
});


// Das Spiel zum ersten Mal laden, wenn die Seite aufgerufen wird.
updateSpiel();

const value = document.querySelector("#ki-tiefe-wert");
const input = document.querySelector("#ki-tiefe-auswahl");
value.textContent = input.value;
input.addEventListener("input", (event) => {
  value.textContent = event.target.value;
});

// In static/script.js

async function animiereZug(startIndex) {
    if (document.body.classList.contains('warten')) return;
    document.body.classList.add('warten');

    // 1. Hole die Start- und Ziel-Elemente
    const startMuldeElem = document.querySelector(`.mulde[data-index='${startIndex}']`);
    const anzahlSteine = parseInt(startMuldeElem.innerText);
    if (anzahlSteine === 0) {
        document.body.classList.remove('warten');
        return;
    }

    // Deaktiviere Klick-Möglichkeiten während der Animation
    const klickbareMulden = document.querySelectorAll('.clickable');
    klickbareMulden.forEach(m => m.classList.remove('clickable'));
    startMuldeElem.innerText = '0'; // Mulde sofort leeren für besseres Gefühl

    // --- NEU: Den korrekten Pfad der Steine VORHER berechnen ---
    const pfad = [];
    let aktuellerIndex = startIndex;
    const gegnerKalahaIndex = 13; // Da der Mensch immer Spieler 1 ist

    // 2. Erstelle und animiere die Steine
    for (let i = 0; i < anzahlSteine; i++) {
        aktuellerIndex = (aktuellerIndex + 1) % 14;
        if (aktuellerIndex === gegnerKalahaIndex) {
            aktuellerIndex = (aktuellerIndex + 1) % 14; // Überspringen
        }
        
        let zielElement;
        if (aktuellerIndex === 6) {
            zielElement = document.getElementById('kalaha-spieler1');
        } else if (aktuellerIndex === 13) {
            zielElement = document.getElementById('kalaha-spieler2');
        } else {
            zielElement = document.querySelector(`.mulde[data-index='${aktuellerIndex}']`);
        }
        pfad.push(zielElement);
    }
    // --- Ende der Pfad-Berechnung ---


    // Starte die Animation für jeden Stein mit einer leichten Verzögerung
    for (let i = 0; i < anzahlSteine; i++) {
        const stein = document.createElement('div');
        stein.className = 'stein';
        document.body.appendChild(stein);

        const startRect = startMuldeElem.getBoundingClientRect();
        const zielRect = pfad[i].getBoundingClientRect();

        // Positioniere Stein am Start
        stein.style.left = `${startRect.left + startRect.width / 2 - 5}px`;
        stein.style.top = `${startRect.top + startRect.height / 2 - 5}px`;
        
        // Timeout für den "Flug" zum berechneten Ziel
        setTimeout(() => {
            const transX = zielRect.left - startRect.left; // + (zielRect.width / 2) - 5;
            const transY = zielRect.top - startRect.top; // + (zielRect.height / 2) - 5;
            stein.style.transform = `translate(${transX}px, ${transY}px)`;
        }, i * 80); // 80ms Verzögerung pro Stein

        // Stein nach der Animation entfernen
        setTimeout(() => {
            stein.remove();
        }, 1000 + i * 80);
    }

    // Am Ende der gesamten Animation den Server kontaktieren
    setTimeout(async () => {
        statusText.innerText = 'KI überlegt...';
        await fetch('/api/mache_zug/' + startIndex);
        await updateSpiel();
        document.body.classList.remove('warten');
    }, anzahlSteine * 180 + 600);
}
