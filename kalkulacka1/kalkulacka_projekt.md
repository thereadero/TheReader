# Kalkulačka (kalkulacka.py)

Tento projekt obsahuje plně funkční kalkulačku postavenou nad knihovnou `tkinter`. Zajišťuje základní aritmetické funkce, přehledné grafické uživatelské rozhraní a robustní zpracování výpočetních operací v reálném čase.

## Co soubor obsahuje

- **`Calculator` třídu**
  Obsahuje výpočetní logiku nezávislou na zobrazení (operace add, subtract, multiply, divide, power, square_root, clear) a ošetřuje kritické chybové stavy jako dělení nulou.
- **`CalculatorApp` třídu**
  - Implementuje grafické rozhraní `tkinter`.
  - Správa zobrazení, rozložení tlačítek (0-9, operace, C, =) a napojení kliknutí na obslužnou logiku výpočtu.

## Jak to vypadá

Rozhraní se skládá z velkého textového pole nahoře pro zobrazení čísel a výsledku a z klasické mřížky tlačítek ve spodní části, pro velmi jednoduché a intuitivní ovládání myší, typické pro standardní softwarové kalkulačky.

## Spuštění programu

Ujistěte se, že máte ve vašem prostředí nainstalovaný Python a podporu pro `tkinter`. Z příkazové řádky spusťte:

```sh
python kalkulacka.py
```

Po spuštění vyskočí okno s grafickým rozhraním kalkulačky, kde můžete okamžitě začít provádět výpočty.
