# Kalkulačka (kalkulacka.py)

Tento projekt obsahuje plně funkční kalkulačku postavenou nad knihovnou `tkinter`. Zajišťuje základní aritmetické funkce, přehledné grafické uživatelské rozhraní a robustní zpracování výpočetních operací v reálném čase.

## Co soubor obsahuje

- **`Calculator` třídu**
  Obsahuje výpočetní logiku nezávislou na zobrazení (operace add, subtract, multiply, divide, power, square_root, clear) a ošetřuje kritické chybové stavy jako dělení nulou a odmocninu ze záporného čísla.
- **`CalculatorApp` třídu**
  - Implementuje grafické rozhraní `tkinter`.
  - Správa zobrazení, rozložení tlačítek a napojení kliknutí na obslužnou logiku výpočtu.
  - Dynamické přizpůsobení délky zobrazeného textu šířce okna pro zamezení přetečení textu.

## Hlavní funkce a vlastnosti rozhraní

- **Shift režim:** Tlačítko **Shift** přepíná mezi základní sadou tlačítek a pokročilejšími matematickými funkcemi.
  - *Standardní režim:* Obsahuje závorky `(`, `)` a desetinnou tečku `.`.
  - *Shift režim:* Zpřístupňuje pokročilé funkce jako `sin(`, `cos(` a `sqrt(`.
- **Dvouřádkový displej (Double Screen):**
  - **Hlavní displej:** Zobrazuje aktuálně zadávaný výraz nebo výsledek.
  - **"Ghost" (historický) displej:** Zobrazuje předchozí zadaný výraz před vyhodnocením (s koncovým `=`), což usnadňuje přehled o výpočtu.
- **Responzivní přizpůsobení:** Při změně velikosti okna kalkulačka automaticky zkracuje výsledek na hlavní obrazovce tak, aby se vešel do viditelné šířky.

## Jak to vypadá

Rozhraní se skládá z dvouřádkového textového pole nahoře pro zobrazení čísel a výsledku a z klasické mřížky tlačítek ve spodní části, pro velmi jednoduché a intuitivní ovládání myší, typické pro standardní softwarové kalkulačky.

## Spuštění programu

Ujistěte se, že máte ve vašem prostředí nainstalovaný Python a podporu pro `tkinter`. Z příkazové řádky spusťte:

```sh
python kalkulacka.py
```

Po spuštění vyskočí okno s grafickým rozhraním kalkulačky, kde můžete okamžitě začít provádět výpočty.
