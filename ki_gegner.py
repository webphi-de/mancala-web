# ki_gegner.py

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
                
                # Das Ergebnis von mache_zug enthält jetzt mehr Infos
                zug_ergebnis = brett_kopie.mache_zug(mulden_index)
                
                # Jetzt rufen wir den MiniMax-Algorithmus auf, um diesen Zug zu bewerten
                # Die KI will ihren Wert maximieren (ist_maximierer = True)
                # Alpha und Beta sind die Startwerte für den Alpha-Beta-Schnitt
                bewertung = self._minimax(
                    brett_kopie, 
                    self.max_tiefe -1, # Tiefe reduzieren für den nächsten Zug im Baum
                    float('-inf'), 
                    float('inf'), 
                    True if zug_ergebnis['hat_extrazug'] else False,
                    # Wir übergeben die Info über den ersten Zug direkt
                    zug_ergebnis['hat_extrazug'],
                    zug_ergebnis['hat_geklaut']
                )
                
                # Wenn diese Bewertung besser ist als die bisher beste, merke sie dir
                if bewertung > beste_bewertung:
                    beste_bewertung = bewertung
                    bester_zug = mulden_index
        
        return bester_zug

    def _minimax(self, brett, tiefe, alpha, beta, ist_maximierer, hat_extrazug=False, hat_geklaut=False):
        # Abbruchbedingung: Tiefe 0 erreicht
        if tiefe == 0:
            return self._bewerte_brett(brett, hat_extrazug, hat_geklaut)
        
        # Abbruchbedingung: Spielende
        if brett.pruefe_spielende():
             return self._bewerte_brett(brett, False, False) # Am Ende gibt es keine Boni mehr

        if ist_maximierer:
            max_bewertung = float('-inf')
            # ... (Mulden-Bereich bestimmen bleibt gleich) ...
            for mulden_index in mulden_bereich:
                if brett.mulden[mulden_index] > 0:
                    brett_kopie = deepcopy(brett)
                    zug_ergebnis = brett_kopie.mache_zug(mulden_index) # Ergebnis holen
                    
                    bewertung = self._minimax(
                        brett_kopie, 
                        tiefe - 1, 
                        alpha, 
                        beta, 
                        True if zug_ergebnis['hat_extrazug'] else False,
                        zug_ergebnis['hat_extrazug'], # Infos für die nächste Ebene weitergeben
                        zug_ergebnis['hat_geklaut']
                    )
                    max_bewertung = max(max_bewertung, bewertung)
                    alpha = max(alpha, bewertung)
                    if beta <= alpha:
                        break 
            return max_bewertung
        else: # Minimierer
            min_bewertung = float('inf')
            # ... (Mulden-Bereich bestimmen bleibt gleich) ...
            for mulden_index in mulden_bereich:
                if brett.mulden[mulden_index] > 0:
                    brett_kopie = deepcopy(brett)
                    zug_ergebnis = brett_kopie.mache_zug(mulden_index) # Ergebnis holen
                    
                    bewertung = self._minimax(
                        brett_kopie, 
                        tiefe - 1, 
                        alpha, 
                        beta, 
                        False if zug_ergebnis['hat_extrazug'] else True,
                        zug_ergebnis['hat_extrazug'], # Infos für die nächste Ebene weitergeben
                        zug_ergebnis['hat_geklaut']
                    )
                    min_bewertung = min(min_bewertung, bewertung)
                    beta = min(beta, bewertung)
                    if beta <= alpha:
                        break
            return min_bewertung
            
    def _bewerte_brett(self, brett, hat_extrazug, hat_geklaut):
        # Hier ist die neue, intelligentere Bewertung!
        if self.spieler_nummer == 1:
            meine_kalaha_idx, gegner_kalaha_idx = 6, 13
            meine_mulden_slice, gegner_mulden_slice = slice(0, 6), slice(7, 13)
        else:
            meine_kalaha_idx, gegner_kalaha_idx = 13, 6
            meine_mulden_slice, gegner_mulden_slice = slice(7, 13), slice(0, 6)
            
        # 1. Die Differenz der Punkte in den Kalahas (wichtigstes Kriterium)
        punkte_bewertung = brett.mulden[meine_kalaha_idx] - brett.mulden[gegner_kalaha_idx]
        
        # 2. Die Differenz der Steine auf dem Feld (mehr Steine = mehr Züge)
        meine_steine_auf_feld = sum(brett.mulden[meine_mulden_slice])
        gegner_steine_auf_feld = sum(brett.mulden[gegner_mulden_slice])
        feld_bewertung = meine_steine_auf_feld - gegner_steine_auf_feld
        
        # 3. Belohnung für strategisch gute Züge
        extrazug_bonus = 3  # Ein Extrazug ist gut
        geklaut_bonus = 5   # Steine klauen ist noch besser
        
        bonus = 0
        if hat_extrazug:
            bonus += extrazug_bonus
        if hat_geklaut:
            bonus += geklaut_bonus
            
        # Die Gesamtbewertung ist eine gewichtete Summe
        # z.B. sind Punkte in der Kalaha doppelt so wichtig wie Steine auf dem Feld
        gesamte_bewertung = (punkte_bewertung * 2) + feld_bewertung + bonus
        
        return gesamte_bewertung