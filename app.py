# app.py

from flask import Flask, jsonify
from spielbrett import Spielbrett
from ki_gegner import KiGegner

# --- Globale Spiel-Variablen ---
app = Flask(__name__)
brett = Spielbrett()
ki = KiGegner(spieler_nummer=2, max_tiefe=5)
aktueller_spieler = 1  # Spieler 1 (Mensch) beginnt

def spiel_zuruecksetzen():
    """Hilfsfunktion, um das Spiel auf den Anfangszustand zu setzen."""
    global brett, aktueller_spieler
    brett = Spielbrett()
    aktueller_spieler = 1

# --- API-Routen ---

@app.route('/')
def home():
    return "Server läuft. Endpunkte: /api/spielstand, /api/neues_spiel, /api/mache_zug/<index>"

@app.route('/api/neues_spiel')
def neues_spiel():
    """Setzt das Spiel zurück und gibt den neuen Spielstand zurück."""
    spiel_zuruecksetzen()
    return get_spielstand()

@app.route('/api/spielstand')
def get_spielstand():
    """Gibt den aktuellen Spielzustand als JSON zurück."""
    spiel_beendet = brett.pruefe_spielende()
    gewinner = None
    if spiel_beendet:
        kalaha1 = brett.mulden[6]
        kalaha2 = brett.mulden[13]
        if kalaha1 > kalaha2: gewinner = 1
        elif kalaha2 > kalaha1: gewinner = 2
        else: gewinner = 0 # Unentschieden

    response_data = {
        'mulden': brett.mulden,
        'aktueller_spieler': aktueller_spieler,
        'spiel_beendet': spiel_beendet,
        'gewinner': gewinner
    }
    return jsonify(response_data)

@app.route('/api/mache_zug/<int:mulden_index>')
def mache_zug_api(mulden_index):
    """Nimmt den Zug des Menschen entgegen und lässt die KI antworten."""
    global aktueller_spieler

    # --- Validierung des menschlichen Zuges ---
    if brett.pruefe_spielende():
        return jsonify({'error': 'Das Spiel ist bereits beendet.'}), 400
    if aktueller_spieler != 1:
        return jsonify({'error': 'Die KI ist am Zug.'}), 400
    if not (0 <= mulden_index <= 5):
        return jsonify({'error': 'Ungültiger Index für Spieler 1.'}), 400
    if brett.mulden[mulden_index] == 0:
        return jsonify({'error': 'Ungültiger Zug, die Mulde ist leer.'}), 400

    # --- Menschlichen Zug ausführen ---
    hat_extrazug_mensch = brett.mache_zug(mulden_index)
    if brett.pruefe_spielende():
        return get_spielstand()
    if hat_extrazug_mensch:
        return get_spielstand() # Mensch hat Extrazug, KI ist nicht dran

    # --- KI-Zug ausführen (wenn sie dran ist) ---
    aktueller_spieler = 2
    while aktueller_spieler == ki.spieler_nummer and not brett.pruefe_spielende():
        ki_zug_index = ki.finde_besten_zug(brett)
        if ki_zug_index == -1: break

        hat_extrazug_ki = brett.mache_zug(ki_zug_index)
        if not hat_extrazug_ki:
            aktueller_spieler = 1 # Spielerwechsel zurück zum Menschen

    return get_spielstand()

# --- Server starten ---
if __name__ == '__main__':
    app.run(debug=True)