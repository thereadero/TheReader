# Dokumentace snake.py

Tento soubor obsahuje hru "Snake" napsanou v Pythonu pomocí pygame.

##  Požadavky

- Python 3 (v projektu je použito virtuální prostředí .venv)
- pygame (nainstalovat např. pip install pygame)

##  Struktura souboru `snake.py`

###  Nastavení okna

    python
    import pygame
    width, height = 500, 500
    win = pygame.display.set_mode((width, height))


- Vytvoří se okno 500×500 px pro vykreslování.

###  Třída (Snake)

Třída reprezentuje hráčovu "hadí" část.

- "x", "y" – souřadnice (levý horní roh) v pixelech
- "width", "height" – velikost obdélníku (10×10)
- "vel" – rychlost (posun v pixelech při každém kroku)

Metoda:

- draw(self, win) – vykreslí zelený obdélník reprezentující hada.

###  Hlavní herní smyčka (main)

Smyčka dělá tyto kroky:

1. Čeká krátký čas ('pygame.time.delay(100)') pro regulaci rychlosti
2. Zpracuje události (uzavření okna)
3. Čte stisknuté šipky a podle toho upraví pozici hada
4. Vymaže obrazovku ('win.fill((0,0,0))')
5. Vykreslí hada a aktualizuje displej ('pygame.display.update()')

Uzavření okna ukončí smyčku a zavolá 'pygame.quit()'.

##  Možná vylepšení

- Omezit pohyb tak, aby had zůstal v rámci okna
- Přidat jídlo a růst hada
- Detekovat srážky sám se sebou
- Přidat skóre a herní restart
- Nastavit konstanty / konfiguraci místo "hardcoded" hodnot
