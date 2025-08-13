# ki_gegner.py

from spielbrett import Spielbrett
from copy import deepcopy

class KiGegner:
    
    def __init__(self, spieler_nummer, max_tiefe=5):
        self.spieler_nummer = spieler_nummer
        self.max_tiefe = max_tiefe

    def finde_besten_zug(self, brett):
        bester_zug = -1
        beste_bewertung = float('-inf')

        if self.spieler_nummer == 1:
            meine_mulden_bereich = range(0, 6)
        else:
            meine_mulden_bereich = range(7, 13)

        for mulden_index in meine_mulden_bereich:
            if brett.mulden[mulden_index] > 0:
                brett_kopie = deepcopy(brett)
                zug_ergebnis = brett_kopie.mache_zug(mulden_index)
                
                bewertung = self._minimax(
                    brett_kopie, 
                    self.max_tiefe - 1, 
                    float('-inf'), 
                    float('inf'), 
                    True if zug_ergebnis['hat_extrazug'] else False,
                    zug_ergebnis['hat_extrazug'],
                    zug_ergebnis['hat_geklaut']
                )
                
                if bewertung > beste_bewertung:
                    beste_bewertung = bewertung
                    bester_zug = mulden_index
        
        return bester_zug

    def _minimax(self, brett, tiefe, alpha, beta, ist_maximierer, hat_extrazug=False, hat_geklaut=False):
        if tiefe == 0 or brett.pruefe_spielende():
            return self._bewerte_brett(brett, hat_extrazug, hat_geklaut)

        if ist_maximierer:
            max_bewertung = float('-inf')
            
            # --- KORREKTUR: Fehlende Logik hier eingefügt ---
            if self.spieler_nummer == 1:
                mulden_bereich = range(0, 6)
            else:
                mulden_bereich = range(7, 13)
            # --- Ende der Korrektur ---

            for mulden_index in mulden_bereich:
                if brett.mulden[mulden_index] > 0:
                    brett_kopie = deepcopy(brett)
                    zug_ergebnis = brett_kopie.mache_zug(mulden_index)
                    
                    bewertung = self._minimax(
                        brett_kopie, 
                        tiefe - 1, 
                        alpha, 
                        beta, 
                        True if zug_ergebnis['hat_extrazug'] else False,
                        zug_ergebnis['hat_extrazug'],
                        zug_ergebnis['hat_geklaut']
                    )
                    max_bewertung = max(max_bewertung, bewertung)
                    alpha = max(alpha, bewertung)
                    if beta <= alpha:
                        break 
            return max_bewertung
        else: # Minimierer
            min_bewertung = float('inf')

            # --- KORREKTUR: Fehlende Logik hier eingefügt ---
            if self.spieler_nummer == 1: # Gegner ist Spieler 2
                mulden_bereich = range(7, 13)
            else: # Gegner ist Spieler 1
                mulden_bereich = range(0, 6)
            # --- Ende der Korrektur ---

            for mulden_index in mulden_bereich:
                if brett.mulden[mulden_index] > 0:
                    brett_kopie = deepcopy(brett)
                    zug_ergebnis = brett_kopie.mache_zug(mulden_index)
                    
                    bewertung = self._minimax(
                        brett_kopie, 
                        tiefe - 1, 
                        alpha, 
                        beta, 
                        False if zug_ergebnis['hat_extrazug'] else True,
                        zug_ergebnis['hat_extrazug'],
                        zug_ergebnis['hat_geklaut']
                    )
                    min_bewertung = min(min_bewertung, bewertung)
                    beta = min(beta, bewertung)
                    if beta <= alpha:
                        break
            return min_bewertung
            
    def _bewerte_brett(self, brett, hat_extrazug, hat_geklaut):
        if self.spieler_nummer == 1:
            meine_kalaha_idx, gegner_kalaha_idx = 6, 13
            meine_mulden_slice, gegner_mulden_slice = slice(0, 6), slice(7, 13)
        else:
            meine_kalaha_idx, gegner_kalaha_idx = 13, 6
            meine_mulden_slice, gegner_mulden_slice = slice(7, 13), slice(0, 6)
            
        punkte_bewertung = brett.mulden[meine_kalaha_idx] - brett.mulden[gegner_kalaha_idx]
        
        meine_steine_auf_feld = sum(brett.mulden[meine_mulden_slice])
        gegner_steine_auf_feld = sum(brett.mulden[gegner_mulden_slice])
        feld_bewertung = meine_steine_auf_feld - gegner_steine_auf_feld
        
        extrazug_bonus = 3
        geklaut_bonus = 5
        
        bonus = 0
        if hat_extrazug:
            bonus += extrazug_bonus
        if hat_geklaut:
            bonus += geklaut_bonus
            
        gesamte_bewertung = (punkte_bewertung * 2) + feld_bewertung + bonus
        
        return gesamte_bewertung