# Dokumentace Snake Game (snake.py)

## Přehled projektu
Tento projekt je rozšířená implementace klasické hry "Had" (Snake) v Pythonu za použití knihovny Pygame. Oproti klasické verzi hra obsahuje plnohodnotné grafické rozhraní, obchod s vylepšeními (Upgrades Tree), systém ukládání/načítání stavu (Saves), nastavení rychlosti a růstu a systém úspěchů (Achievements).

---

## Technické požadavky
- **Python 3.x** (v projektu je předpřipraveno virtuální prostředí `.venv`)
- **Pygame** (instalace pomocí `pip install pygame`)

---

## Herní mechanismy a vlastnosti

### 1. Rozhraní a menu
Hra běží v okně o velikosti **800×500 px** s vykreslovanou vodicí mřížkou (velikost buňky je **20×20 px**).
Hlavní menu obsahuje následující sekce:
- **Start**: Spustí samotnou hru.
- **Upgrades Tree**: Obchod s vylepšeními.
- **Saves**: Správa uložených pozic.
- **Achievements**: Seznam herních úspěchů.
- **Settings**: Nastavení hry (odemkne se po zakoupení příslušných vylepšení).
- **Exit**: Ukončení aplikace.

### 2. Hratelnost a jídlo
- Had (zelená barva) začíná na souřadnicích `(240, 240)`.
- Na ploše se současně generuje **3 až 4 červená jídla** na náhodných pozicích zarovnaných do mřížky.
- Každé snědené jídlo přičte **1 bod** do skóre.
- Pokud had narazí sám do sebe (nebo do zdi bez aktivního vylepšení *Wall Wrap*), hra končí, skóre se resetuje na 0 a had se vrátí do výchozího stavu.

### 3. Strom vylepšení (Upgrades Tree)
Skóre získané ve hře slouží jako platidlo v obchodě s vylepšeními. Zakoupením vylepšení se body odečtou:
- **Wall Wrap (Procházení zdmi) – cena: 200 bodů**:
  - Umožňuje hadovi procházet okraji obrazovky (při opuštění pravého okraje se objeví vlevo atd.).
- **Speed Setting (Nastavení rychlosti) – cena: 100 bodů**:
  - Odemkne posuvník (Slider) v nastavení, kterým lze regulovat rychlost hry od 1 (nejpomalejší) do 50 (nejrychlejší).
- **Disable Growth (Vypnutí růstu) – cena: 75 bodů**:
  - Odemkne přepínač v nastavení, kterým lze vypnout zvětšování hada po snědení jídla (skóre se stále přičítá).

### 4. Systém ukládání a načítání (Saves)
Hra podporuje plnohodnotné ukládání stavu do souboru `saves.json` v adresáři projektu:
- Během hry lze stisknout **klávesu `L`**, která otevře obrazovku pro pojmenování a uložení pozice (ukládá se pozice hada a aktuální skóre).
- V menu **Saves**:
  - **Levé kliknutí** na název uložení načte hru a pokračuje se ze uložené pozice.
  - **Pravé kliknutí** na název uložení vyvolá potvrzovací dialog pro smazání uložení.

### 5. Systém úspěchů (Achievements)
Úspěchy se trvale ukládají do souboru `achievements.json`:
- **Century Maker (Stovkař)**: Odemkne se po dosažení skóre **100**. V menu Achievements svítí zeleně jako `[Unlocked]`.

---

## Ovládání

### Hlavní menu a navigace
- **Levé tlačítko myši**: Výběr a klikání na tlačítka/položky.
- **Tlačítko "Back" / klávesa `ESC`**: Návrat do předchozího menu.

### Během hry (Gameplay)
- **Pohyb hada**: Šipky (`Nahoru`, `Dolů`, `Doleva`, `Doprava`) nebo klávesy `W`, `A`, `S`, `D`.
- **Uložení hry**: Klávesa `L` (otevře dialog uložení).

---

## Struktura kódu (`snake.py`)

Kód je rozdělen do několika tříd a funkcí:
- **`Button`**: Zajišťuje vykreslování tlačítek a detekci kliknutí myší.
- **`Slider`**: Implementuje posuvník pro nastavení rychlosti v menu nastavení (využívá drag-and-drop myší).
- **`Snake`**: Spravuje tělo hada jako seznam souřadnic segmentů `body = [(x, y)]`, směr pohybu a vykreslování těla.
- **`Food`**: Třída reprezentující jídlo na ploše s metodou `new_pos()` pro náhodné přemístění na mřížce.
- **`load_saves() / save_state()`**: Zajišťují ukládání a načítání herních pozic ze souboru `saves.json`.
- **`load_achievements() / save_achievements()`**: Správa souboru `achievements.json`.
- **`spawn_foods()`**: Pomocná funkce generující 3 až 4 nová jídla na začátku nebo při vyprázdnění plochy.
- **`main()`**: Hlavní herní smyčka obsluhující stavy hry (`menu`, `game`, `upgrades`, `saves`, `save_name`, `settings`, `achievements`), vstupy z klávesnice, pohyb, kolize a překreslování okna.

