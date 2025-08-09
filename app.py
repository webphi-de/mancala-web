# app.py

# render_template wurde hinzugefügt
from flask import Flask, jsonify, render_template
from spielbrett import Spielbrett
from ki_gegner import KiGegner

# --- Globale Spiel-Variablen ---
app = Flask(__name__)
brett = Spielbrett()
ki = KiGegner(spieler_nummer=2, max_tiefe=5)
aktueller_spieler = 1
spiel_verlauf = []

def spiel_zuruecksetzen():
    """Hilfsfunktion, um das Spiel auf den Anfangszustand zu setzen."""
    global brett, aktueller_spieler, spiel_verlauf 
    brett = Spielbrett()
    aktueller_spieler = 1
    spiel_verlauf = []
    

# --- API-Routen und die neue HTML-Route ---

@app.route('/')
def home():
    """Liefert jetzt unsere Haupt-HTML-Seite aus."""
    return render_template('index.html')

@app.route('/api/verlauf')
def get_verlauf():
    return jsonify(spiel_verlauf)

@app.route('/api/neues_spiel')
def neues_spiel():
    spiel_zuruecksetzen()
    return get_spielstand()

@app.route('/api/spielstand')
def get_spielstand():
    spiel_beendet = brett.pruefe_spielende()
    gewinner = None
    if spiel_beendet:
        kalaha1 = brett.mulden[6]
        kalaha2 = brett.mulden[13]
        if kalaha1 > kalaha2: gewinner = 1
        elif kalaha2 > kalaha1: gewinner = 2
        else: gewinner = 0

    response_data = {
        'mulden': brett.mulden,
        'aktueller_spieler': aktueller_spieler,
        'spiel_beendet': spiel_beendet,
        'gewinner': gewinner
    }
    return jsonify(response_data)

@app.route('/api/mache_zug/<int:mulden_index>')
def mache_zug_api(mulden_index):
    global aktueller_spieler, spiel_verlauf

    # --- 1. Validierung des menschlichen Zuges (bleibt gleich) ---
    if brett.pruefe_spielende():
        return jsonify({'error': 'Das Spiel ist bereits beendet.'}), 400
    if aktueller_spieler != 1:
        return jsonify({'error': 'Die KI ist am Zug.'}), 400
    if not (0 <= mulden_index <= 5):
        return jsonify({'error': 'Ungültiger Index für Spieler 1.'}), 400
    if brett.mulden[mulden_index] == 0:
        return jsonify({'error': 'Ungültiger Zug, die Mulde ist leer.'}), 400

    # --- 2. Menschlichen Zug EINMAL ausführen und protokollieren ---
    steine_vorher = brett.mulden[mulden_index]
    zug_ergebnis = brett.mache_zug(mulden_index) # EINZIGER AUFRUF FÜR MENSCH
    
    log_eintrag = f"   Mulde {mulden_index + 1} ({steine_vorher}) -> Mulde {zug_ergebnis['letzter_index']+1}"
    spiel_verlauf.append(log_eintrag)

    # --- 3. Spielende oder Extrazug prüfen ---
    if brett.pruefe_spielende():
        return get_spielstand()
    if zug_ergebnis['hat_extrazug']:
        #spiel_verlauf.append("Mensch hat einen Extrazug!")
        return get_spielstand() # Zug beenden, Mensch bleibt dran

    # --- 4. KI-Zug(e) ausführen, wenn sie dran ist ---
    aktueller_spieler = 2
    while aktueller_spieler == ki.spieler_nummer and not brett.pruefe_spielende():
        ki_zug_index = ki.finde_besten_zug(brett)
        if ki_zug_index == -1: break # KI kann nicht ziehen

        steine_vorher_ki = brett.mulden[ki_zug_index]
        zug_ergebnis_ki = brett.mache_zug(ki_zug_index) # EINZIGER AUFRUF FÜR KI
        
        # KORREKTUR: ki_zug_index und zug_ergebnis_ki verwenden
        log_eintrag_ki = f"KI: Mulde {ki_zug_index+1} ({steine_vorher_ki}) -> Mulde {zug_ergebnis_ki['letzter_index']+1}"
        spiel_verlauf.append(log_eintrag_ki)

        if brett.pruefe_spielende():
            break # Spielende nach KI-Zug prüfen
        
        if zug_ergebnis_ki['hat_extrazug']:
            #spiel_verlauf.append("KI hat einen Extrazug!")
            continue # Die while-Schleife läuft erneut, KI bleibt dran
        else:
            aktueller_spieler = 1 # Spielerwechsel zum Menschen, Schleife endet

    return get_spielstand()

# --- Server starten ---
if __name__ == '__main__':
    app.run(debug=True)