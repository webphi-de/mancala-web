# app.py

import os
from flask import Flask, jsonify, render_template, request, session
from spielbrett import Spielbrett
from ki_gegner import KiGegner

app = Flask(__name__)
# Ein geheimer Schlüssel ist für die Nutzung von Sessions zwingend erforderlich.
# In einer echten Produktionsumgebung sollte dieser komplex und geheim sein.
app.secret_key = os.urandom(24) 

# --- Routen ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/spielstand')
def get_spielstand():
    # Prüfen, ob ein Spiel in der Session existiert
    if 'mulden' not in session:
        # Falls nicht, ein neues Spiel initialisieren (z.B. mit Standardwerten)
        spiel_zuruecksetzen(starter=1, max_tiefe=5)
        
    # Spielobjekte aus den Session-Daten bei jeder Anfrage neu erstellen
    brett = Spielbrett()
    brett.mulden = session['mulden']
    
    spiel_beendet = brett.pruefe_spielende()
    gewinner = None
    if spiel_beendet:
        kalaha1 = brett.mulden[6]
        kalaha2 = brett.mulden[13]
        if kalaha1 > kalaha2: gewinner = 1
        elif kalaha2 > kalaha1: gewinner = 2
        else: gewinner = 0
        
        # Spielstand nach Ende des Spiels in der Session aktualisieren
        session['mulden'] = brett.mulden

    response_data = {
        'mulden': brett.mulden,
        'aktueller_spieler': session.get('aktueller_spieler'),
        'spiel_beendet': spiel_beendet,
        'gewinner': gewinner
    }
    return jsonify(response_data)

@app.route('/api/mache_zug/<int:mulden_index>')
def mache_zug_api(mulden_index):
    # Spielobjekte aus der Session laden
    brett = Spielbrett()
    brett.mulden = session['mulden']
    ki = KiGegner(spieler_nummer=2, max_tiefe=session.get('max_tiefe', 5))
    aktueller_spieler = session.get('aktueller_spieler')
    spiel_verlauf = session.get('spiel_verlauf', [])

    # 1. Validierung
    if brett.pruefe_spielende():
        return jsonify({'error': 'Das Spiel ist bereits beendet.'}), 400
    if aktueller_spieler != 1:
        return jsonify({'error': 'Die KI ist am Zug.'}), 400
    if not (0 <= mulden_index <= 5) or brett.mulden[mulden_index] == 0:
        return jsonify({'error': 'Ungültiger Zug.'}), 400

    # 2. Menschlichen Zug ausführen und protokollieren
    steine_vorher = brett.mulden[mulden_index]
    zug_ergebnis = brett.mache_zug(mulden_index)
    log_eintrag = f"   Mulde {mulden_index + 1} ({steine_vorher}) ➨ Mulde {zug_ergebnis['letzter_index']+1}"
    spiel_verlauf.append(log_eintrag)

    # 3. Spielende oder Extrazug prüfen
    if brett.pruefe_spielende() or zug_ergebnis['hat_extrazug']:
        # Spielzustand in Session speichern und aktuellen Stand zurückgeben
        session['mulden'] = brett.mulden
        session['spiel_verlauf'] = spiel_verlauf
        session['aktueller_spieler'] = 1 # Mensch bleibt dran
        return get_spielstand()

    # 4. KI-Zug(e)
    aktueller_spieler = 2
    while aktueller_spieler == ki.spieler_nummer and not brett.pruefe_spielende():
        ki_zug_index = ki.finde_besten_zug(brett)
        if ki_zug_index == -1: break

        steine_vorher_ki = brett.mulden[ki_zug_index]
        zug_ergebnis_ki = brett.mache_zug(ki_zug_index)
        log_eintrag_ki = f"KI: Mulde {ki_zug_index-6} ({steine_vorher_ki}) ➠ Mulde {zug_ergebnis_ki['letzter_index']+1}"
        spiel_verlauf.append(log_eintrag_ki)

        if brett.pruefe_spielende(): break
        if zug_ergebnis_ki['hat_extrazug']: continue
        
        aktueller_spieler = 1
    
    # Finalen Zustand nach allen Zügen in der Session speichern
    session['mulden'] = brett.mulden
    session['spiel_verlauf'] = spiel_verlauf
    session['aktueller_spieler'] = aktueller_spieler
    
    return get_spielstand()

@app.route('/api/neues_spiel', methods=['POST'])
def neues_spiel():
    # Werte aus dem Request Body (JSON) holen
    data = request.get_json()
    starter = int(data.get('starter', 1))
    max_tiefe = int(data.get('max_tiefe', 5))
    
    spiel_zuruecksetzen(starter, max_tiefe)
    return get_spielstand()

@app.route('/api/verlauf')
def get_verlauf():
    return jsonify(session.get('spiel_verlauf', []))

# --- Hilfsfunktionen ---

def spiel_zuruecksetzen(starter=1, max_tiefe=5):
    brett = Spielbrett()
    ki = KiGegner(spieler_nummer=2, max_tiefe=max_tiefe)
    aktueller_spieler = starter
    spiel_verlauf = []

    # Wenn die KI startet
    if aktueller_spieler == ki.spieler_nummer:
        while aktueller_spieler == ki.spieler_nummer and not brett.pruefe_spielende():
            ki_zug_index = ki.finde_besten_zug(brett)
            if ki_zug_index == -1: break
            
            steine_vorher_ki = brett.mulden[ki_zug_index]
            zug_ergebnis_ki = brett.mache_zug(ki_zug_index)
            log_eintrag_ki = f"KI: Mulde {ki_zug_index-6} ({steine_vorher_ki}) Mulde {zug_ergebnis_ki['letzter_index']+1}"
            spiel_verlauf.append(log_eintrag_ki)
            
            if brett.pruefe_spielende(): break
            if not zug_ergebnis_ki['hat_extrazug']:
                aktueller_spieler = 1
    
    # Den neuen Spielzustand in der Session speichern
    session['mulden'] = brett.mulden
    session['aktueller_spieler'] = aktueller_spieler
    session['spiel_verlauf'] = spiel_verlauf
    session['max_tiefe'] = max_tiefe


# --- Server starten ---
if __name__ == '__main__':
    # Wir starten den Server ohne einen initialen Spiel-Reset,
    # da dies nun pro Session geschieht.
    app.run(host='192.168.178.24', port=5000, debug=True)