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
        self.root.configure(bg="#1e1e2e")
        self.current_tokens = []
        self.current_errors = []
        self.setup_styles()
        self.build_header()
        self.build_workspace()
        self.build_status_bar()
        self.load_sample(self.VALID_SAMPLE)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#282a36",
            foreground="#f8f8f2",
            fieldbackground="#282a36",
            rowheight=26,
            font=("Consolas", 10),
        )
        style.configure(
            "Treeview.Heading",
            background="#44475a",
            foreground="#f8f8f2",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Treeview", background=[("selected", "#6272a4")])

    def make_button(self, parent, text, bg, fg, cmd):
        return tk.Button(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=9,
            pady=5,
            cursor="hand2",
            command=cmd,
        )

    def build_header(self):
        header = tk.Frame(self.root, bg="#181825", pady=10, padx=15)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="MiniLang Function-Call Lexical Analyzer",
            font=("Segoe UI", 14, "bold"),
            bg="#181825",
            fg="#cba6f7",
        ).pack(side=tk.LEFT)

        btn_frame = tk.Frame(header, bg="#181825")
        btn_frame.pack(side=tk.RIGHT)
        self.make_button(btn_frame, "▶ Analyze", "#a6e3a1", "#11111b", self.analyze_code).pack(side=tk.LEFT, padx=3)
        self.make_button(
            btn_frame,
            "Valid Sample",
            "#89b4fa",
            "#11111b",
            lambda: self.load_sample(self.VALID_SAMPLE),
        ).pack(side=tk.LEFT, padx=3)
        self.make_button(
            btn_frame,
            "Error Sample",
            "#fab387",
            "#11111b",
            lambda: self.load_sample(self.ERROR_SAMPLE),
        ).pack(side=tk.LEFT, padx=3)
        self.make_button(btn_frame, "Open File", "#cdd6f4", "#11111b", self.open_file).pack(side=tk.LEFT, padx=3)
        self.make_button(btn_frame, "Export Results", "#f9e2af", "#11111b", self.export_results).pack(side=tk.LEFT, padx=3)
        self.make_button(btn_frame, "Clear", "#f38ba8", "#11111b", self.clear_all).pack(side=tk.LEFT, padx=3)

    def build_workspace(self):
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#1e1e2e", sashwidth=6)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        left_frame = tk.Frame(main_pane, bg="#1e1e2e")
        tk.Label(
            left_frame,
            text="MiniLang Source Code Input",
            font=("Segoe UI", 10, "bold"),
            bg="#1e1e2e",
            fg="#cdd6f4",
        ).pack(anchor="w", pady=(0, 5))
        self.code_editor = tk.Text(
            left_frame,
            font=("Consolas", 11),
            bg="#282a36",
            fg="#f8f8f2",
            insertbackground="#f8f8f2",
            padx=10,
            pady=10,
            bd=0,
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        main_pane.add(left_frame, width=410)

        right_pane = tk.PanedWindow(main_pane, orient=tk.VERTICAL, bg="#1e1e2e", sashwidth=6)

        token_frame = tk.Frame(right_pane, bg="#1e1e2e")
        self.token_header = tk.Label(
            token_frame,
            text="Recognized Tokens (0)",
            font=("Segoe UI", 10, "bold"),
            bg="#1e1e2e",
            fg="#a6e3a1",
        )
        self.token_header.pack(anchor="w", pady=(0, 5))
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

        error_frame = tk.Frame(right_pane, bg="#1e1e2e")
        self.error_header = tk.Label(
            error_frame,
            text="Lexical Errors (0)",
            font=("Segoe UI", 10, "bold"),
            bg="#1e1e2e",
            fg="#f38ba8",
        )
        self.error_header.pack(anchor="w", pady=(0, 5))
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
            bg="#181825",
            fg="#a6adc8",
            anchor="w",
            padx=12,
            pady=5,
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