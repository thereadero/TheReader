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
        
        for i in range(4):
            self.root.columnconfigure(i, weight=1)
        self.root.rowconfigure(0, weight=4)
        for i in range(1, 6):
            self.root.rowconfigure(i, weight=1)

        self.calc = Calculator()
        self.expression = ""
        self.is_shift = False
        
        # Screen frame
        self.screen_frame = tk.Frame(root, bg="white", bd=2, relief="sunken")
        self.screen_frame.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
        self.screen_frame.columnconfigure(0, weight=1)
        self.screen_frame.rowconfigure(0, weight=1)
        self.screen_frame.rowconfigure(1, weight=3)

        self.ghost_var = tk.StringVar()
        self.ghost_screen = tk.Entry(self.screen_frame, textvariable=self.ghost_var, font=('Arial', 14), bg="white", fg="gray", justify="right", bd=0, highlightthickness=0)
        self.ghost_screen.grid(row=0, column=0, sticky="nsew", padx=8, pady=(5, 0))

        self.screen_var = tk.StringVar()
        self.screen = tk.Entry(self.screen_frame, textvariable=self.screen_var, font=('Arial', 24), bg="white", justify="right", bd=0, highlightthickness=0)
        self.screen.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 5))
        
        self.render_buttons()

    def render_buttons(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()

        if self.is_shift:
            buttons = [
                'Shift', 'sin(', 'cos(', 'C',
                '7', '8', '9', '/',
                '4', '5', '6', '*',
                '1', '2', '3', '-',
                '0', 'sqrt(', '=', '+'
            ]
        else:
            buttons = [
                'Shift', '(', ')', 'C',
                '7', '8', '9', '/',
                '4', '5', '6', '*',
                '1', '2', '3', '-',
                '0', '.', '=', '+'
            ]

        row_val = 1
        col_val = 0
        for button in buttons:
            action = lambda x=button: self.click(x)
            tk.Button(self.root, text=button, font=('Arial', 14), cursor="hand2", command=action).grid(row=row_val, column=col_val, padx=5, pady=5, sticky="nsew")
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

    def click(self, item):
        if item == 'Shift':
            self.is_shift = not self.is_shift
            self.render_buttons()
            return
            
        if item == 'C':
            self.expression = ""
            self.screen_var.set("")
            self.ghost_var.set("")
        elif item == '=':
            try:
                # Upravený výpočet evaluací pro základní funkce
                eval_expr = self.expression.replace('sin', 'math.sin').replace('cos', 'math.cos').replace('sqrt', 'math.sqrt')
                result = str(eval(eval_expr))
                self.ghost_var.set(self.expression + " =")
                self.screen_var.set(result)
                self.expression = result
            except Exception:
                self.ghost_var.set(self.expression + " =")
                self.screen_var.set("Error")
                self.expression = ""
        else:
            if self.screen_var.get() == "Error":
                self.expression = ""
                self.ghost_var.set("")
            self.expression += str(item)
            self.screen_var.set(self.expression)

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()