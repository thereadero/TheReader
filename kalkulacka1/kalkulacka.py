# jednoduchá kalkulačka s funkcemi pro základní aritmetické operace, mocniny a odmocniny
import math

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
if __name__ == "__main__":
    calc = Calculator()
    print("Welcome to the Calculator!")
    while True:
        try:
# uživatelský vstup pro výběr operace a čísel, s ošetřením neplatných vstupů            
            operation = input("Enter operation (add, subtract, multiply, divide, power, sqrt, clear) or 'exit' to quit: ")
            if operation == 'exit':
                print("Goodbye!")
                break
            elif operation == 'clear':
                print(f"Result cleared. Current result: {calc.clear()}")
            elif operation in ['add', 'subtract', 'multiply', 'divide', 'power']:
                a = float(input("Enter first number: "))
                b = float(input("Enter second number: "))
                if operation == 'add':
                    print(f"Result: {calc.add(a, b)}")
                elif operation == 'subtract':
                    print(f"Result: {calc.subtract(a, b)}")
                elif operation == 'multiply':
                    print(f"Result: {calc.multiply(a, b)}")
                elif operation == 'divide':
                    print(f"Result: {calc.divide(a, b)}")
                elif operation == 'power':
                    print(f"Result: {calc.power(a, b)}")
            elif operation == 'sqrt':
                a = float(input("Enter number: "))
                print(f"Result: {calc.square_root(a)}")
            else:
                print("Invalid operation. Please try again.")
        except ValueError as e:
            print(f"Error: {e}. Please try again.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Please try again.")