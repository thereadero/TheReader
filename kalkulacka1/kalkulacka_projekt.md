# Kalkulačka (kalkulacka.py)

Tento modul obsahuje jednoduchou kalkulačku (`Calculator`) poskytující základní aritmetické operace, mocniny a odmocniny spolu s jednoduchým interaktivním rozhraním uživatele.

##  Co soubor obsahuje

- `Calculator` třídu se stavem `result` (poslední výsledek).
- Metody pro základní operace:
  - `add(a, b)` – sčítání
  - `subtract(a, b)` – odčítání
  - `multiply(a, b)` – násobení
  - `divide(a, b)` – dělení (vyvolá `ValueError` při dělení nulou)
  - `power(a, b)` – mocnina (a^b)
  - `square_root(a)` – odmocnina (vyvolá `ValueError` pro záporná čísla)
  - `clear()` – vynuluje `result` (návratová hodnota je 0)

##  Jak použít (jako knihovnu)

```python
from calculator import Calculator

calc = Calculator()
print(calc.add(1, 2))          # 3
print(calc.subtract(5, 3))     # 2
print(calc.multiply(4, 2.5))   # 10.0
print(calc.divide(10, 2))      # 5.0
print(calc.power(2, 8))        # 256.0
print(calc.square_root(25))    # 5.0

calc.clear()                  # resetuje výsledek na 0
```

>  `divide(a, b)` vyhodí `ValueError`, pokud je `b == 0`.

>  `square_root(a)` vyhodí `ValueError`, pokud je `a < 0`.

## 🖥️ Spuštění jako skript (příkazová řádka)

Spusťte:

```sh
python calculator.py
```

Poté můžete v interaktivním režimu zadávat operace:

- `add`, `subtract`, `multiply`, `divide`, `power`, `sqrt`, `clear`
- `exit` pro ukončení

### Příklad interakce

```
Enter operation (add, subtract, multiply, divide, power, sqrt, clear) or 'exit' to quit: add
Enter first number: 1
Enter second number: 2
Result: 3.0
```
