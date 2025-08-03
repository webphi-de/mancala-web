# ki_gegner.py

# Wir müssen die Spielbrett-Klasse kennen, um damit arbeiten zu können.
# Und wir brauchen die `deepcopy` Funktion, um das Brett für Simulationen zu kopieren.
from spielbrett import Spielbrett
from copy import deepcopy

class KiGegner:
    
    def __init__(self, spieler_nummer, max_tiefe=5):
        """
        Initialisiert den KI-Gegner.
        spieler_nummer: 1 oder 2
        max_tiefe: Wie viele Züge die KI maximal vorausschauen soll.
        """
        self.spieler_nummer = spieler_nummer
        self.max_tiefe = max_tiefe

    def finde_besten_zug(self, brett):
        """
        Die Hauptmethode, die von außen aufgerufen wird.
        Sie startet den MiniMax-Algorithmus für alle möglichen Züge.
        """
        bester_zug = -1
        beste_bewertung = float('-inf') # Startet mit der schlechtestmöglichen Bewertung

        # Hier werden wir alle möglichen Züge des KI-Spielers durchgehen...
        # ...für jeden Zug den MiniMax-Algorithmus aufrufen...
        # ...und uns den Zug mit der besten Bewertung merken.
        
        # Diese Methode füllen wir gleich mit Leben.
        pass

        return bester_zug

    def _minimax(self, brett, tiefe, alpha, beta, ist_maximierer):
        """
        Die rekursive Kernfunktion des Algorithmus.
        _minimax, weil sie eine "interne" Hilfsmethode ist.
        """
        # Hier kommt die Logik rein:
        # 1. Abbruchbedingung: Tiefe erreicht oder Spielende? Dann Brett bewerten.
        # 2. Wenn Maximierer-Runde:
        #    - Durch alle Züge gehen
        #    - Rekursiv _minimax für jeden Zug aufrufen (als Minimierer)
        #    - Den höchsten Wert finden und Alpha-Beta-Schnitt anwenden
        # 3. Wenn Minimierer-Runde:
        #    - Das Gleiche, nur umgekehrt.
        
        # Auch diese Methode füllen wir gleich.
        pass

    def _bewerte_brett(self, brett):
        """
        Die Heuristik! Das "Gehirn" der KI.
        Bewertet einen gegebenen Spielzustand aus der Sicht der KI.
        Eine einfache, aber gute erste Heuristik ist:
        "Anzahl meiner Steine in der Kalaha - Anzahl der Steine des Gegners"
        """
        if self.spieler_nummer == 1:
            meine_kalaha_idx = 6
            gegner_kalaha_idx = 13
        else:
            meine_kalaha_idx = 13
            gegner_kalaha_idx = 6
            
        bewertung = brett.mulden[meine_kalaha_idx] - brett.mulden[gegner_kalaha_idx]
        return bewertung