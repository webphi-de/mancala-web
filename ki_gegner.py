# ki_gegner.py

from spielbrett import Spielbrett
from copy import deepcopy

class KiGegner:
    
    def __init__(self, spieler_nummer, max_tiefe=9):
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
        # Die beste Bewertung muss für den Maximierer initial die schlechteste sein
        # Und für den Minimierer (wenn die KI Extrazug hatte und wieder Maximierer ist)
        # müssen wir das nachher noch berücksichtigen.
        beste_bewertung = float('-inf')

        # Bestimmen, welche Mulden der KI gehören
        if self.spieler_nummer == 1:
            meine_mulden_bereich = range(0, 6)   # Indizes 0 bis 5
            gegner_mulden_bereich = range(7, 13) # Indizes 7 bis 13
        else: # self.spieler_nummer == 2
            meine_mulden_bereich = range(7, 13) # Indizes 7 bis 12
            gegner_mulden_bereich = range(0, 6) # Indizes 0 bis 5

        # Iteriere über alle möglichen Mulden, die die KI wählen könnte
        for mulden_index in meine_mulden_bereich:
            # Nur legale Züge betrachten: Mulde darf nicht leer sein
            if brett.mulden[mulden_index] > 0:
                # Brett kopieren, um den Zug zu simulieren, ohne das Original zu ändern
                brett_kopie = deepcopy(brett)
                
                # Zug auf der Kopie ausführen
                # Die mache_zug Methode gibt zurück, ob ein Extrazug erfolgt ist.
                # Für die KI-Bewertung ist das wichtig, da es die "Ist_Maximierer"-Ebene beeinflusst.
                # Hier nehmen wir an, dass mache_zug nur True/False für Extrazug zurückgibt.
                # Wir müssen später anpassen, dass mache_zug keine Prints macht und keine Returns bei Fehlern.
                hat_extrazug = brett_kopie.mache_zug(mulden_index)
                
                # Jetzt rufen wir den MiniMax-Algorithmus auf, um diesen Zug zu bewerten
                # Die KI will ihren Wert maximieren (ist_maximierer = True)
                # Alpha und Beta sind die Startwerte für den Alpha-Beta-Schnitt
                bewertung = self._minimax(
                    brett_kopie, 
                    self.max_tiefe -1, # Tiefe reduzieren für den nächsten Zug im Baum
                    float('-inf'), 
                    float('inf'), 
                    True if hat_extrazug else False # ist_maximierer für den Zustand NACH dem ersten Zug
                                                    # Wenn Extrazug, bleibt die KI am Zug (Maximierer)
                                                    # Wenn keiner, ist der gegner am Zug (Minimierer)
                )
                
                # Wenn diese Bewertung besser ist als die bisher beste, merke sie dir
                if bewertung > beste_bewertung:
                    beste_bewertung = bewertung
                    bester_zug = mulden_index
        
        return bester_zug

    def _minimax(self, brett, tiefe, alpha, beta, ist_maximierer):
        """
        Die rekursive Kernfunktion des Algorithmus. _minimax, weil sie eine "interne" Hilfsmethode ist.
        """
        # 1. Abbruchbedingungen
        # a) Maximale Tiefe erreicht
        if tiefe == 0:
            return self._bewerte_brett(brett)
        
        # b) Spiel ist beendet
        # Prüfe, ob das Spielende erreicht ist. Wenn ja, bewerte das Endbrett.
        # Hier ist es wichtig, dass pruefe_spielende() das Brett auch anpasst (Steine in Kalaha verschieben)
        # bevor wir es bewerten.
        if brett.pruefe_spielende():
             return self._bewerte_brett(brett)

        # 2. Wenn der Maximierer am Zug ist (unsere KI)
        if ist_maximierer:
            max_bewertung = float('-inf')
            
            # Bestimmen der möglichen Züge für den Maximierer
            if self.spieler_nummer == 1: # KI ist Spieler 1
                mulden_bereich = range(0, 6)
            else: # KI ist Spieler 2
                mulden_bereich = range(7, 13)

            for mulden_index in mulden_bereich:
                if brett.mulden[mulden_index] > 0: # Nur legale Züge
                    brett_kopie = deepcopy(brett)
                    hat_extrazug = brett_kopie.mache_zug(mulden_index)
                    
                    # Rekursiver Aufruf:
                    # Wenn Extrazug: bleibt der Maximierer am Zug (ist_maximierer = True)
                    # Wenn kein Extrazug: wechselt zum Minimierer (ist_maximierer = False)
                    bewertung = self._minimax(
                        brett_kopie, 
                        tiefe - 1, 
                        alpha, 
                        beta, 
                        True if hat_extrazug else False # Perspektive des NÄCHSTEN Spielers
                    )
                    max_bewertung = max(max_bewertung, bewertung)
                    alpha = max(alpha, bewertung)
                    
                    # Alpha-Beta-Schnitt: Wenn Alpha größer als Beta, dann schneiden
                    if beta <= alpha:
                        break # Pruning
            return max_bewertung

        # 3. Wenn der Minimierer am Zug ist (der Gegner aus Sicht der KI)
        else: 
            min_bewertung = float('inf')

            # Bestimmen der möglichen Züge für den Minimierer (Gegner)
            if self.spieler_nummer == 1: # KI ist Spieler 1, Gegner ist Spieler 2
                mulden_bereich = range(7, 13)
            else: # KI ist Spieler 2, Gegner ist Spieler 1
                mulden_bereich = range(0, 6)

            for mulden_index in mulden_bereich:
                if brett.mulden[mulden_index] > 0: # Nur legale Züge
                    brett_kopie = deepcopy(brett)
                    hat_extrazug = brett_kopie.mache_zug(mulden_index)
                    
                    # Rekursiver Aufruf:
                    # Wenn Extrazug: bleibt der Minimierer am Zug (ist_maximierer = False)
                    # Wenn kein Extrazug: wechselt zum Maximierer (ist_maximierer = True)
                    bewertung = self._minimax(
                        brett_kopie, 
                        tiefe - 1, 
                        alpha, 
                        beta, 
                        False if hat_extrazug else True # Perspektive des NÄCHSTEN Spielers
                    )
                    min_bewertung = min(min_bewertung, bewertung)
                    beta = min(beta, bewertung)
                    
                    # Alpha-Beta-Schnitt: Wenn Beta kleiner als Alpha, dann schneiden
                    if beta <= alpha:
                        break # Pruning
            return min_bewertung
            
    def _bewerte_brett(self, brett):
        """
        Die Heuristik! Das "Gehirn" der KI.
        Bewertet einen gegebenen Spielzustand aus der Sicht der KI.
        Verbesserte Version
        """
        if self.spieler_nummer == 1:
            meine_kalaha_idx = 6
            gegner_kalaha_idx = 13
            meine_mulden_slice = slice(0, 6)
            gegner_mulden_slice = slice(7, 13)
        else:
            meine_kalaha_idx = 13
            gegner_kalaha_idx = 6
            meine_mulden_slice = slice(7, 13)
            gegner_mulden_slice = slice(0, 6)   
            
        # Faktor 1: Die Differenz der Punkte in den Kalahas (wichtigstes Kriterium)
        punkte_bewertung = brett.mulden[meine_kalaha_idx] - brett.mulden[gegner_kalaha_idx]
        
        # Faktor 2: Die Differenz der Steine auf der jeweiligen Spielfeldseite
        # Mehr Steine auf der eigenen Seite bedeuten mehr zukünftige Möglichkeiten.
        meine_steine_auf_feld = sum(brett.mulden[meine_mulden_slice])
        gegner_steine_auf_feld = sum(brett.mulden[gegner_mulden_slice])
        feld_bewertung = meine_steine_auf_feld - gegner_steine_auf_feld
        
        # Die Gesamtbewertung ist eine gewichtete Summe.
        # Wir gewichten die Punkte in der Kalaha deutlich höher als die Steine auf dem Feld.
        # z.B. im Verhältnis 2:1 oder 3:1
        gesamte_bewertung = (punkte_bewertung * 2) + feld_bewertung
        
        return gesamte_bewertung