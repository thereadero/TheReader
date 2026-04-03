# jednoduchá kalkulačka s funkcemi pro základní aritmetické operace, mocniny a odmocniny
import math
import tkinter as tk

# Remove the blocking GUI code from top
class Calculator:
    def __init__(self):
        self.result = 0
# sčítací operace
    def add(self, a, b):
        self.result = a + b
        return self.result
# odčítací operace
    def subtract(self, a, b):
        self.result = a - b
        return self.result
# násobící operace
    def multiply(self, a, b):
        self.result = a * b
        return self.result
# dělicí operace s ošetřením dělení nulou
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        self.result = a / b
        return self.result
# mocninná operace
    def power(self, a, b):
        self.result = math.pow(a, b)
        return self.result
# odmocninná operace s ošetřením záporných čísel
    def square_root(self, a):
        if a < 0:
            raise ValueError("Cannot take square root of negative number")
        self.result = math.sqrt(a)
        return self.result
    def clear(self):
        self.result = 0
        return self.result
class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kalkulačka")
        self.root.configure(background="gray")
        self.root.geometry("320x450+50+50")
        
        self.calc = Calculator()
        self.expression = ""
        
        # Screen
        self.screen_var = tk.StringVar()
        self.screen = tk.Entry(root, textvariable=self.screen_var, font=('Arial', 24), bg="white", justify="right")
        self.screen.grid(row=0, column=0, columnspan=4, ipadx=8, ipady=20, pady=10, padx=10, sticky="ew")
        
        # Buttons for numbers and basic operations
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            'C', '0', '=', '+'
        ]
        
        row_val = 1
        col_val = 0
        for button in buttons:
            action = lambda x=button: self.click(x)
            tk.Button(root, text=button, width=5, height=2, font=('Arial', 14), command=action).grid(row=row_val, column=col_val, padx=5, pady=5)
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

    def click(self, item):
        if item == 'C':
            self.expression = ""
            self.screen_var.set("")
        elif item == '=':
            try:
                # Zjednodušený výpočet evaluací
                result = str(eval(self.expression))
                self.screen_var.set(result)
                self.expression = result
            except Exception:
                self.screen_var.set("Error")
                self.expression = ""
        else:
            if self.screen_var.get() == "Error":
                self.expression = ""
            self.expression += str(item)
            self.screen_var.set(self.expression)

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()