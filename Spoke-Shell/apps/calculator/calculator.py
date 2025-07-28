import tkinter as tk
import math
import matplotlib.pyplot as plt
import numpy as np

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Spoke Calculator")
        self.root.geometry("370x550")
        self.root.configure(bg="#121212")
        self.expression = ""
        self.history = []
        self.memory = 0
        self.variables = {}

        self.create_widgets()
        self.root.bind("<Key>", self.keypress)

    def create_widgets(self):
        # Top Frame: Display + History + Graph
        top_frame = tk.Frame(self.root, bg="#121212")
        top_frame.pack(fill="x", padx=10, pady=10)

        self.display = tk.Entry(
            top_frame,
            font=("Consolas", 22),
            bg="#121212",
            fg="#ffffff",
            insertbackground="white",
            relief="flat",
            borderwidth=0,
            justify="right"
        )
        self.display.pack(side="left", fill="x", expand=True, ipady=10)

        hist_btn = tk.Button(
            top_frame,
            text="≡",
            command=self.show_history,
            font=("Consolas", 16),
            bg="#1e1e1e",
            fg="#66b2ff",
            bd=0,
            width=3,
            height=1,
            relief="flat",
            activebackground="#0044aa",
            activeforeground="white"
        )
        hist_btn.pack(side="right", padx=(5, 0))

        graph_btn = tk.Button(
            top_frame,
            text="📈",
            command=self.graph_expression,
            font=("Consolas", 16),
            bg="#1e1e1e",
            fg="#66b2ff",
            bd=0,
            width=3,
            height=1,
            relief="flat",
            activebackground="#0044aa",
            activeforeground="white"
        )
        graph_btn.pack(side="right", padx=(5, 5))

        # Button layout
        buttons = [
            ["C", "(", ")", "DEL"],
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"],
            ["sqrt", "log", "sin", "cos"],
            ["tan", "^", "M+", "M-"],
            ["MR", "MC", "x", "y"]
        ]

        button_frame = tk.Frame(self.root, bg="#121212")
        button_frame.pack(expand=True, fill="both")

        for row_vals in buttons:
            row = tk.Frame(button_frame, bg="#121212")
            row.pack(expand=True, fill="both")
            for val in row_vals:
                if val == "":
                    tk.Label(row, text="", bg="#121212").pack(side="left", expand=True, fill="both", padx=1, pady=1)
                else:
                    b = tk.Button(
                        row,
                        text=val,
                        command=lambda x=val: self.on_button_click(x),
                        font=("Consolas", 16),
                        bg="#1e1e1e",
                        fg="#66b2ff" if not val.isdigit() and val not in ["."] else "#ffffff",
                        bd=0,
                        relief="flat",
                        activebackground="#0044aa",
                        activeforeground="white"
                    )
                    b.pack(side="left", expand=True, fill="both", padx=1, pady=1)

    def keypress(self, event):
        if event.char in "0123456789.+-*/()=^":
            self.expression += event.char
        elif event.keysym == "Return":
            self.calculate()
        elif event.keysym == "BackSpace":
            self.expression = self.expression[:-1]
        elif event.keysym == "Escape":
            self.expression = ""
        self.update_display()

    def on_button_click(self, value):
        if value == "=":
            self.calculate()
        elif value == "C":
            self.expression = ""
        elif value == "DEL":
            self.expression = self.expression[:-1]
        elif value == "M+":
            result = self.safe_eval(self.expression)
            if result is not None:
                self.memory += result
        elif value == "M-":
            result = self.safe_eval(self.expression)
            if result is not None:
                self.memory -= result
        elif value == "MR":
            self.expression += str(self.memory)
        elif value == "MC":
            self.memory = 0
        elif value in ["sqrt", "log", "sin", "cos", "tan"]:
            self.expression += f"{value}("
        elif value == "^":
            self.expression += "**"
        else:
            self.expression += value
        self.update_display()

    def update_display(self):
        self.display.delete(0, tk.END)
        self.display.insert(0, self.expression)

    def calculate(self):
        expr = self.expression.strip()
        if "=" in expr:
            var, val = map(str.strip, expr.split("=", 1))
            result = self.safe_eval(val)
            if result is not None and var.isidentifier():
                self.variables[var] = result
                self.history.append(f"{var} = {result}")
                self.expression = str(result)
        else:
            result = self.safe_eval(expr)
            if result is not None:
                self.history.append(f"{expr} = {result}")
                self.expression = str(result)
        self.update_display()

    def safe_eval(self, expr):
        try:
            # Allow user variables and math functions
            allowed = {
                "sqrt": math.sqrt,
                "log": math.log10,
                "sin": lambda x: math.sin(math.radians(x)),
                "cos": lambda x: math.cos(math.radians(x)),
                "tan": lambda x: math.tan(math.radians(x)),
                **self.variables
            }
            return eval(expr, {"__builtins__": {}}, allowed)
        except Exception as e:
            self.expression = "Error"
            return None

    def show_history(self):
        history_win = tk.Toplevel(self.root)
        history_win.title("History")
        history_win.geometry("300x300")
        history_win.configure(bg="#1e1e1e")

        listbox = tk.Listbox(
            history_win,
            font=("Consolas", 14),
            bg="#1e1e1e",
            fg="#ffffff",
            selectbackground="#0044aa"
        )
        listbox.pack(expand=True, fill="both", padx=10, pady=10)

        for entry in reversed(self.history):
            listbox.insert(tk.END, entry)

        def insert_from_history(event):
            selection = listbox.curselection()
            if selection:
                expr = listbox.get(selection[0]).split("=")[0].strip()
                self.expression = expr
                self.update_display()
                history_win.destroy()

        listbox.bind("<Double-Button-1>", insert_from_history)

    def graph_expression(self):
        expr = self.expression.strip()
        if "y=" in expr or expr.startswith("y ="):
            expr = expr.split("=")[-1].strip()
        try:
            x_vals = np.linspace(-10, 10, 400)
            allowed = {
                "sqrt": np.sqrt,
                "log": np.log10,
                "sin": np.sin,
                "cos": np.cos,
                "tan": np.tan,
                "pi": np.pi,
                "e": np.e,
                **self.variables
            }
            y_vals = [eval(expr, {"__builtins__": {}}, {**allowed, "x": x}) for x in x_vals]
            plt.plot(x_vals, y_vals, label=f"y = {expr}")
            plt.title(f"Graph of y = {expr}")
            plt.xlabel("x")
            plt.ylabel("y")
            plt.grid(True)
            plt.legend()
            plt.show()
        except Exception as e:
            self.expression = "Graph Error"
            self.update_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()
