class Spielbrett:
    def __init__(self):
        # Index 0-5: Mulden Spieler 1
        # Index 6:  Kalaha Spieler 1
        # Index 7-12: Mulden Spieler 2
        # Index 13: Kalaha Spieler 2
        
        # Korrekter Startzustand mit 6 Bohnen pro Spielmulde
        self.mulden = [6, 6, 6, 6, 6, 6, 0, 6, 6, 6, 6, 6, 6, 0]

    def __str__(self):
        # Eine einfache Methode, um das Brett auf der Konsole auszugeben
        # Wir können das später noch schöner formatieren
        brett_str = f"    {self.mulden[12]:>2} {self.mulden[11]:>2} {self.mulden[10]:>2} {self.mulden[9]:>2} {self.mulden[8]:>2} {self.mulden[7]:>2}\n"
        brett_str += f"{self.mulden[13]:>2} [ S P I E L E R  2 ] {self.mulden[6]:>2}\n"
        brett_str += f"    {self.mulden[0]:>2} {self.mulden[1]:>2} {self.mulden[2]:>2} {self.mulden[3]:>2} {self.mulden[4]:>2} {self.mulden[5]:>2}"
        return brett_str

    def mache_zug(self, mulden_index):
        # --- 1. Vorbereitungen und Zug-Validierung ---

        # Anhand des Index bestimmen, welcher Spieler am Zug ist.
        # Spieler 1: Mulden 0-5, Kalaha 6
        # Spieler 2: Mulden 7-12, Kalaha 13
        if 0 <= mulden_index <= 5:
            spieler_kalaha = 6
            gegner_kalaha = 13
        elif 7 <= mulden_index <= 12:
            spieler_kalaha = 13
            gegner_kalaha = 6
        else:
            print("Fehler: Ungültiger Index. Bitte eine Spielmulde (0-5 oder 7-12) wählen.")
            return # Zug beenden

        # Prüfen, ob die gewählte Mulde leer ist.
        steine_in_hand = self.mulden[mulden_index]
        if steine_in_hand == 0:
            print("Fehler: Die gewählte Mulde ist leer.")
            return # Zug beenden

        # Gewählte Mulde leeren
        self.mulden[mulden_index] = 0

        # --- 2. Das Aussäen der Steine ---

        aktueller_index = mulden_index
        while steine_in_hand > 0:
            # Zum nächsten Index wechseln, das Brett ist zyklisch (14 Mulden, 0-13)
            aktueller_index = (aktueller_index + 1) % 14

            # Die Kalaha des Gegners wird übersprungen!
            if aktueller_index == gegner_kalaha:
                continue # Nächste Iteration der Schleife starten

            # Einen Stein in die aktuelle Mulde legen
            self.mulden[aktueller_index] += 1
            steine_in_hand -= 1

        # Der letzte Index ist der, wo der letzte Stein gelandet ist
        letzter_index = aktueller_index

        # --- 3. Regeln nach dem Zug anwenden ---

        # Regel A: Letzter Stein landet in der eigenen Kalaha -> Extrazug
        if letzter_index == spieler_kalaha:
            print("Letzter Stein in eigener Kalaha. Extrazug!")
            return # Nichts weiter zu tun, Spieler ist erneut dran

        # Regel B: Letzter Stein landet in einer leeren Mulde auf der eigenen Seite -> Steine klauen
        # Wir prüfen, ob die Mulde vorher leer war (jetzt ist 1 Stein drin) und ob sie auf der Spielerseite liegt.
        auf_eigener_seite = (0 <= letzter_index <= 5) if spieler_kalaha == 6 else (7 <= letzter_index <= 12)

        if self.mulden[letzter_index] == 1 and auf_eigener_seite:
            # Index der gegenüberliegenden Mulde berechnen
            gegenueber_index = 12 - letzter_index
            
            # Prüfen, ob in der gegenüberliegenden Mulde Steine liegen
            if self.mulden[gegenueber_index] > 0:
                print(f"Geklaut! Steine aus Mulde {gegenueber_index} werden erobert.")
                # Eigene Steine und die des Gegners in die Kalaha legen
                geklaute_steine = self.mulden[gegenueber_index] + self.mulden[letzter_index]
                self.mulden[spieler_kalaha] += geklaute_steine
                
                # Die beiden Mulden leeren
                self.mulden[letzter_index] = 0
                self.mulden[gegenueber_index] = 0
        
        # Ansonsten ist der Zug einfach normal zu Ende.
        print("Zug beendet. Nächster Spieler ist an der Reihe.")

    def pruefe_spielende(self):
        # Summe der Steine auf den Seiten beider Spieler berechnen.
        # Python-Slicing: self.mulden[0:6] nimmt die Elemente von Index 0 bis 5.
        summe_spieler1 = sum(self.mulden[0:6])
        summe_spieler2 = sum(self.mulden[7:13])

        # Prüfen, ob die Seite eines Spielers leer ist.
        if summe_spieler1 == 0 or summe_spieler2 == 0:
            # Ja, das Spiel ist zu Ende.
            
            # Die restlichen Steine des Gegners seiner Kalaha hinzufügen.
            self.mulden[6] += summe_spieler1
            self.mulden[13] += summe_spieler2

            # Alle Spielmulden leeren.
            for i in range(6):
                self.mulden[i] = 0
                self.mulden[i + 7] = 0
            
            # Signal geben, dass das Spiel vorbei ist.
            return True 

        # Wenn keine Seite leer ist, geht das Spiel weiter.
        return False


# --- Komplette Spiel-Schleife zum Testen ---
if __name__ == '__main__':
    brett = Spielbrett()
    aktueller_spieler = 1 # Spieler 1 beginnt

    while True: # Die Schleife läuft, bis das Spiel endet
        print("\n" + "="*30)
        print(brett)
        print(f"\nSpieler {aktueller_spieler} ist am Zug.")

        # Zug des Spielers einlesen
        try:
            # Wir fragen nach einer Zahl von 1-6 und rechnen sie in den Index um
            if aktueller_spieler == 1:
                wahl = int(input("Wähle deine Mulde (1-6): "))
                mulden_index = wahl - 1
            else: # Spieler 2
                wahl = int(input("Wähle deine Mulde (1-6 auf deiner Seite): "))
                mulden_index = wahl + 6 # Umrechnung auf Indizes 7-12
            
            brett.mache_zug(mulden_index)

        except (ValueError, IndexError):
            print("Ungültige Eingabe. Bitte eine passende Zahl eingeben.")
            continue # Nächster Versuch in der Schleife

        # Nach jedem Zug prüfen, ob das Spiel vorbei ist
        if brett.pruefe_spielende():
            print("\n" + "="*30)
            print("Das Spiel ist beendet!")
            print(brett)
            kalaha1 = brett.mulden[6]
            kalaha2 = brett.mulden[13]
            print(f"\nEndstand: Spieler 1 ({kalaha1}) vs. Spieler 2 ({kalaha2})")
            if kalaha1 > kalaha2:
                print("Spieler 1 gewinnt!")
            elif kalaha2 > kalaha1:
                print("Spieler 2 gewinnt!")
            else:
                print("Unentschieden!")
            break # Die while-Schleife beenden

        # Spieler wechseln (außer bei Extrazug, diese Logik müssen wir noch verfeinern)
        # Fürs Erste wechseln wir einfach immer den Spieler
        aktueller_spieler = 2 if aktueller_spieler == 1 else 1