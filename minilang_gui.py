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
        self.build_workspace()
        self.build_status_bar()
        self.load_sample(self.VALID_SAMPLE)

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

    def build_workspace(self):
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        left_frame = tk.Frame(main_pane)
        tk.Label(
            left_frame,
            text="MiniLang Source Code Input",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        self.code_editor = tk.Text(left_frame, font=("Consolas", 11), padx=8, pady=8)
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        main_pane.add(left_frame, width=410)

        right_pane = tk.PanedWindow(main_pane, orient=tk.VERTICAL, sashwidth=5)

        token_frame = tk.Frame(right_pane)
        self.token_header = tk.Label(
            token_frame,
            text="Recognized Tokens (0)",
            font=("Segoe UI", 10, "bold"),
        )
        self.token_header.pack(anchor="w", pady=(0, 4))
        self.token_tree = ttk.Treeview(
            token_frame,
            columns=("idx", "line", "col", "lexeme", "type"),
            show="headings",
        )
        for col, title, w in [
            ("idx", "#", 40),
            ("line", "Line", 50),
            ("col", "Col", 50),
            ("lexeme", "Lexeme", 180),
            ("type", "Token Category", 160),
        ]:
            self.token_tree.heading(col, text=title)
            self.token_tree.column(
                col,
                width=w,
                anchor="center" if col in {"idx", "line", "col"} else "w",
            )
        self.token_tree.pack(fill=tk.BOTH, expand=True)
        right_pane.add(token_frame, height=270)

        error_frame = tk.Frame(right_pane)
        self.error_header = tk.Label(
            error_frame,
            text="Lexical Errors (0)",
            font=("Segoe UI", 10, "bold"),
        )
        self.error_header.pack(anchor="w", pady=(0, 4))
        self.error_tree = ttk.Treeview(
            error_frame,
            columns=("idx", "line", "col", "lexeme", "msg"),
            show="headings",
            height=4,
        )
        for col, title, w in [
            ("idx", "#", 40),
            ("line", "Line", 50),
            ("col", "Col", 50),
            ("lexeme", "Invalid Lexeme", 130),
            ("msg", "Error Description", 230),
        ]:
            self.error_tree.heading(col, text=title)
            self.error_tree.column(
                col,
                width=w,
                anchor="center" if col in {"idx", "line", "col"} else "w",
            )
        self.error_tree.pack(fill=tk.BOTH, expand=True)
        right_pane.add(error_frame)
        main_pane.add(right_pane)

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
        lexer = MiniLangLexer(self.code_editor.get("1.0", tk.END))
        self.current_tokens, self.current_errors = lexer.tokenize()
        for row in self.token_tree.get_children():
            self.token_tree.delete(row)
        for row in self.error_tree.get_children():
            self.error_tree.delete(row)
        for idx, tok in enumerate(self.current_tokens, 1):
            self.token_tree.insert("", tk.END, values=(idx, tok.line, tok.column, tok.lexeme, tok.type))
        for idx, err in enumerate(self.current_errors, 1):
            self.error_tree.insert("", tk.END, values=(idx, err.line, err.column, err.lexeme, err.message))
        self.token_header.config(text=f"Recognized Tokens ({len(self.current_tokens)})")
        self.error_header.config(text=f"Lexical Errors ({len(self.current_errors)})")
        self.status_var.set(
            f"Analysis complete: {len(self.current_tokens)} tokens, {len(self.current_errors)} errors."
        )

    def load_sample(self, text):
        self.code_editor.delete("1.0", tk.END)
        self.code_editor.insert("1.0", text)
        self.analyze_code()

    def clear_all(self):
        self.code_editor.delete("1.0", tk.END)
        self.analyze_code()

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("MiniLang", "*.minilang *.txt"), ("All", "*.*")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.load_sample(f.read())

    def export_results(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("Text", "*.txt")])
        if path:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Status", "Line", "Col", "Lexeme", "Type/Error", "Trace"])
                for t in self.current_tokens:
                    writer.writerow(["VALID", t.line, t.column, t.lexeme, t.type, " | ".join(t.trace)])
                for e in self.current_errors:
                    writer.writerow(["ERROR", e.line, e.column, e.lexeme, e.message, " | ".join(e.trace)])


if __name__ == "__main__":
    root = tk.Tk()
    MiniLangGUI(root)
    root.mainloop()