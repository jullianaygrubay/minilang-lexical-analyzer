import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from lexer import MiniLangLexer


class MiniLangGUI:
    VALID_SAMPLE = """START
    // Define a function
    FUNCTION greet(student: STR, score: INT) -> VOID {
        display(student, score);
        RETURN;
    }
    LET status = check_grade(95);
    greet("Alex", 95);
END"""

    ERROR_SAMPLE = """START
    display("CS302", 100);
    123func("Ana");
    display("Unclosed string);
    add(5 + 3);
    LET x = 95.50;
END"""

    def __init__(self, root):
        self.root = root
        self.root.title("MiniLang Lexical Analyzer & DFA Tracer — CS302")
        self.root.geometry("1180x700")
        self.current_tokens = []
        self.current_errors = []
        self.build_header()
        self.build_status_bar()

    def make_button(self, parent, text, cmd):
        return tk.Button(parent, text=text, padx=8, pady=4, command=cmd)

    def build_header(self):
        header = tk.Frame(self.root, padx=10, pady=8)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="MiniLang Function-Call Lexical Analyzer",
            font=("Segoe UI", 13, "bold"),
        ).pack(side=tk.LEFT)

        btn_frame = tk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        self.make_button(btn_frame, "Analyze", self.analyze_code).pack(side=tk.LEFT, padx=3)
        self.make_button(
            btn_frame,
            "Valid Sample",
            lambda: self.load_sample(self.VALID_SAMPLE),
        ).pack(side=tk.LEFT, padx=3)
        self.make_button(
            btn_frame,
            "Error Sample",
            lambda: self.load_sample(self.ERROR_SAMPLE),
        ).pack(side=tk.LEFT, padx=3)
        self.make_button(btn_frame, "Open File", self.open_file).pack(side=tk.LEFT, padx=3)
        self.make_button(btn_frame, "Export Results", self.export_results).pack(side=tk.LEFT, padx=3)
        self.make_button(btn_frame, "Clear", self.clear_all).pack(side=tk.LEFT, padx=3)

    def build_status_bar(self):
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            padx=10,
            pady=4,
        ).pack(fill=tk.X, side=tk.BOTTOM)

    def analyze_code(self):
        pass

    def load_sample(self, text):
        pass

    def open_file(self):
        pass

    def export_results(self):
        pass

    def clear_all(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    MiniLangGUI(root)
    root.mainloop()