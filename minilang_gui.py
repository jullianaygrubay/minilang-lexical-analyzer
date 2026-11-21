import csv
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from lexer import MiniLangLexer

import sys
from pathlib import Path

def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path

class LineNumberCanvas(tk.Canvas):
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.fg_color = "#6272a4"

    def redraw(self, *args):
        self.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            self.create_text(
                36,
                dline[1],
                anchor="ne",
                text=i.split(".")[0],
                fill=self.fg_color,
                font=("Consolas", 11),
            )
            i = self.text_widget.index(f"{i}+1line")


class MiniLangGUI:
    THEMES = {
        "dark": {
            "bg": "#1e1e2e",
            "header_bg": "#181825",
            "title_fg": "#cba6f7",
            "label_fg": "#cdd6f4",
            "status_fg": "#a6adc8",
            "editor_bg": "#282a36",
            "editor_fg": "#f8f8f2",
            "editor_select": "#44475a",
            "gutter_bg": "#21222c",
            "gutter_fg": "#6272a4",
            "tree_bg": "#282a36",
            "tree_fg": "#f8f8f2",
            "tree_head_bg": "#44475a",
            "tree_head_fg": "#f8f8f2",
            "tree_select": "#6272a4",
            "trace_bg": "#181825",
            "trace_fg": "#89dceb",
            "token_header": "#a6e3a1",
            "error_header": "#f38ba8",
            "error_bg": "#3b232c",
            "kw": "#ff79c6",
            "id": "#8be9fd",
            "str": "#f1fa8c",
            "num": "#bd93f9",
            "op": "#ffb86c",
            "delim": "#f8f8f2",
            "comment": "#6272a4",
            "toggle_text": "☀ Light Mode",
            "toggle_bg": "#f9e2af",
        },
        "light": {
            "bg": "#eff1f5",
            "header_bg": "#dce0e8",
            "title_fg": "#8839ef",
            "label_fg": "#4c4f69",
            "status_fg": "#5c5f77",
            "editor_bg": "#ffffff",
            "editor_fg": "#4c4f69",
            "editor_select": "#ccd0da",
            "gutter_bg": "#e6e9ef",
            "gutter_fg": "#8c8fa1",
            "tree_bg": "#ffffff",
            "tree_fg": "#4c4f69",
            "tree_head_bg": "#ccd0da",
            "tree_head_fg": "#4c4f69",
            "tree_select": "#bcc0cc",
            "trace_bg": "#e6e9ef",
            "trace_fg": "#04a5e5",
            "token_header": "#40a02b",
            "error_header": "#d20f39",
            "error_bg": "#f5d0d6",
            "kw": "#d20f39",
            "id": "#1e66f5",
            "str": "#df8e1d",
            "num": "#8839ef",
            "op": "#fe640b",
            "delim": "#4c4f69",
            "comment": "#9ca0b0",
            "toggle_text": "🌙 Dark Mode",
            "toggle_bg": "#cba6f7",
        },
    }

    VALID_SAMPLE = """START
    // Define a function
    FUNCTION greet(student: STR, score: INT) -> VOID {
        display(student, score);
        RETURN;
    }

    // Call functions inside main block
    LET status = check_grade(95);
    greet("Alex", 95);
END"""

    ERROR_SAMPLE = """START
    // Valid function call
    display("CS302", 100);

    // Intentional lexical errors for testing
    123func("Ana");
    display("Unclosed string);
    add(5 + 3);
    LET x = 95.50;
END"""

    def __init__(self, root):
        self.root = root
        self.root.title("MiniLang Lexical Analyzer & DFA Tracer — CS302")
        self.root.geometry("1220x720")

        self.current_theme = "dark"
        self.current_tokens = []
        self.current_errors = []
        self.analyze_after_id = None
        self.last_trace_is_error = False

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.build_ui()
        self.apply_theme()
        self.bind_shortcuts()
        self.load_sample(self.VALID_SAMPLE)

    def build_ui(self):
        # Top Header Bar
        self.header = tk.Frame(self.root, pady=10, padx=15)
        self.header.pack(fill=tk.X)

        self.title_label = tk.Label(
            self.header,
            text="MiniLang Function-Call Lexical Analyzer",
            font=("Segoe UI", 14, "bold"),
        )
        self.title_label.pack(side=tk.LEFT)

        self.btn_frame = tk.Frame(self.header)
        self.btn_frame.pack(side=tk.RIGHT)

        self.make_button(self.btn_frame, "▶ Analyze", "#a6e3a1", "#11111b", self.analyze_code).pack(side=tk.LEFT, padx=3)
        self.make_button(self.btn_frame, "Valid Sample", "#89b4fa", "#11111b", lambda: self.load_sample(self.VALID_SAMPLE)).pack(side=tk.LEFT, padx=3)
        self.make_button(self.btn_frame, "Error Sample", "#fab387", "#11111b", lambda: self.load_sample(self.ERROR_SAMPLE)).pack(side=tk.LEFT, padx=3)
        self.make_button(self.btn_frame, "Open File", "#cdd6f4", "#11111b", self.open_file).pack(side=tk.LEFT, padx=3)
        self.make_button(self.btn_frame, "Export Results", "#94e2d5", "#11111b", self.export_results).pack(side=tk.LEFT, padx=3)
        self.make_button(self.btn_frame, "Clear", "#f38ba8", "#11111b", self.clear_all).pack(side=tk.LEFT, padx=3)

        # Theme Toggle Button
        self.theme_btn = self.make_button(
            self.btn_frame, "☀ Light Mode", "#f9e2af", "#11111b", self.toggle_theme
        )
        self.theme_btn.pack(side=tk.LEFT, padx=(8, 0))

        # Main Split Container
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=6)
        self.main_pane.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # LEFT PANE: Editor + Line Number Gutter
        self.left_frame = tk.Frame(self.main_pane)
        self.editor_label = tk.Label(
            self.left_frame,
            text="MiniLang Source Code Input (Live Auto-Analyze)",
            font=("Segoe UI", 10, "bold"),
        )
        self.editor_label.pack(anchor="w", pady=(0, 5))

        self.editor_container = tk.Frame(self.left_frame, bd=1)
        self.editor_container.pack(fill=tk.BOTH, expand=True)

        self.code_editor = tk.Text(
            self.editor_container,
            font=("Consolas", 11),
            undo=True,
            padx=10,
            pady=10,
            bd=0,
        )
        self.code_editor.tag_configure("keyword", font=("Consolas", 11, "bold"))
        self.code_editor.tag_configure("comment", font=("Consolas", 11, "italic"))
        self.code_editor.tag_configure("lexical_error", underline=True)

        self.line_numbers = LineNumberCanvas(
            self.editor_container, self.code_editor, width=44, highlightthickness=0, bd=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.editor_container, command=self.on_editor_scroll)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_editor.config(yscrollcommand=self.on_text_yscroll)

        self.code_editor.bind("<KeyRelease>", self.on_editor_key_release)
        for event in ("<MouseWheel>", "<ButtonRelease-1>", "<Configure>"):
            self.code_editor.bind(event, self.line_numbers.redraw)

        self.main_pane.add(self.left_frame, width=430)

        # RIGHT PANE: Output Panels
        self.right_pane = tk.PanedWindow(self.main_pane, orient=tk.VERTICAL, sashwidth=6)

        self.token_frame = tk.Frame(self.right_pane)
        self.token_header = tk.Label(
            self.token_frame,
            text="Recognized Tokens (0) — Click any row to inspect DFA trace",
            font=("Segoe UI", 10, "bold"),
        )
        self.token_header.pack(anchor="w", pady=(0, 5))

        tree_container = tk.Frame(self.token_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        self.token_tree = ttk.Treeview(tree_container, columns=("idx", "line", "col", "lexeme", "type"), show="headings")
        for col, title, w in [("idx", "#", 40), ("line", "Line", 50), ("col", "Col", 50), ("lexeme", "Lexeme", 180), ("type", "Token Category", 160)]:
            self.token_tree.heading(col, text=title)
            self.token_tree.column(col, width=w, anchor="center" if col in {"idx", "line", "col"} else "w")

        self.token_tree.bind("<<TreeviewSelect>>", self.on_token_select)
        tree_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.token_tree.yview)
        self.token_tree.configure(yscrollcommand=tree_scroll.set)
        self.token_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_pane.add(self.token_frame, height=275)

        self.trace_frame = tk.Frame(self.right_pane)
        self.trace_header = tk.Label(
            self.trace_frame,
            text="DFA State Transition Trace",
            font=("Segoe UI", 10, "bold"),
        )
        self.trace_header.pack(anchor="w", pady=(0, 5))
        self.trace_box = tk.Text(
            self.trace_frame, font=("Consolas", 10), height=5, padx=10, pady=8, bd=0, state=tk.DISABLED
        )
        self.trace_box.pack(fill=tk.BOTH, expand=True)
        self.right_pane.add(self.trace_frame, height=150)

        self.error_frame = tk.Frame(self.right_pane)
        self.error_header = tk.Label(
            self.error_frame,
            text="Lexical Errors (0) — Click any row to inspect error path & jump to line",
            font=("Segoe UI", 10, "bold"),
        )
        self.error_header.pack(anchor="w", pady=(0, 5))

        err_container = tk.Frame(self.error_frame)
        err_container.pack(fill=tk.BOTH, expand=True)

        self.error_tree = ttk.Treeview(err_container, columns=("idx", "line", "col", "lexeme", "msg"), show="headings", height=4)
        for col, title, w in [("idx", "#", 40), ("line", "Line", 50), ("col", "Col", 50), ("lexeme", "Invalid Lexeme", 130), ("msg", "Error Description", 230)]:
            self.error_tree.heading(col, text=title)
            self.error_tree.column(col, width=w, anchor="center" if col in {"idx", "line", "col"} else "w")

        self.error_tree.bind("<<TreeviewSelect>>", self.on_error_select)
        err_scroll = ttk.Scrollbar(err_container, orient=tk.VERTICAL, command=self.error_tree.yview)
        self.error_tree.configure(yscrollcommand=err_scroll.set)
        self.error_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        err_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_pane.add(self.error_frame)
        self.main_pane.add(self.right_pane)

        # Status Bar
        self.status_var = tk.StringVar(value="Ready.")
        self.status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            padx=12,
            pady=5,
            font=("Segoe UI", 9),
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()

    def apply_theme(self):
        t = self.THEMES[self.current_theme]

        # Root, panes & frames
        self.root.configure(bg=t["bg"])
        self.header.configure(bg=t["header_bg"])
        self.btn_frame.configure(bg=t["header_bg"])
        self.title_label.configure(bg=t["header_bg"], fg=t["title_fg"])
        self.theme_btn.configure(text=t["toggle_text"], bg=t["toggle_bg"])

        for pane in (self.main_pane, self.right_pane):
            pane.configure(bg=t["bg"])
        for frame in (self.left_frame, self.token_frame, self.trace_frame, self.error_frame):
            frame.configure(bg=t["bg"])

        # Labels & status bar
        self.editor_label.configure(bg=t["bg"], fg=t["label_fg"])
        self.token_header.configure(bg=t["bg"], fg=t["token_header"])
        self.error_header.configure(bg=t["bg"], fg=t["error_header"])
        self.trace_header.configure(
            bg=t["bg"], fg=t["error_header"] if self.last_trace_is_error else t["trace_fg"]
        )
        self.status_bar.configure(bg=t["header_bg"], fg=t["status_fg"])

        # Editor & line numbers
        self.editor_container.configure(bg=t["tree_head_bg"])
        self.code_editor.configure(
            bg=t["editor_bg"],
            fg=t["editor_fg"],
            insertbackground=t["editor_fg"],
            selectbackground=t["editor_select"],
        )
        self.line_numbers.configure(bg=t["gutter_bg"])
        self.line_numbers.fg_color = t["gutter_fg"]
        self.line_numbers.redraw()

        # Editor syntax & error tags
        self.code_editor.tag_configure("keyword", foreground=t["kw"])
        self.code_editor.tag_configure("string", foreground=t["str"])
        self.code_editor.tag_configure("number", foreground=t["num"])
        self.code_editor.tag_configure("operator", foreground=t["op"])
        self.code_editor.tag_configure("comment", foreground=t["comment"])
        self.code_editor.tag_configure("lexical_error", foreground=t["error_header"], background=t["error_bg"])
        self.code_editor.tag_raise("string")
        self.code_editor.tag_raise("comment")
        self.code_editor.tag_raise("lexical_error")

        # Trace box
        self.trace_box.configure(
            bg=t["trace_bg"],
            fg=t["error_header"] if self.last_trace_is_error else t["trace_fg"],
        )

        # Treeview tables & category colors
        self.style.configure(
            "Treeview",
            background=t["tree_bg"],
            foreground=t["tree_fg"],
            fieldbackground=t["tree_bg"],
            rowheight=26,
            font=("Consolas", 10),
        )
        self.style.configure(
            "Treeview.Heading",
            background=t["tree_head_bg"],
            foreground=t["tree_head_fg"],
            font=("Segoe UI", 10, "bold"),
        )
        self.style.map("Treeview", background=[("selected", t["tree_select"])])

        for tag, color_key in [
            ("KEYWORD", "kw"),
            ("IDENTIFIER", "id"),
            ("STRING_LITERAL", "str"),
            ("INT_LITERAL", "num"),
            ("ASSIGN_OP", "op"),
            ("RETURN_ARROW", "op"),
            ("DELIMITER", "delim"),
        ]:
            self.token_tree.tag_configure(tag, foreground=t[color_key])
        self.error_tree.tag_configure("ERROR", foreground=t["error_header"])

    def bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.export_results())
        self.root.bind("<Control-t>", lambda e: self.toggle_theme())
        self.root.bind("<Control-Return>", lambda e: self.analyze_code())

    def make_button(self, parent, text, bg_color, fg_color, command):
        return tk.Button(
            parent,
            text=text,
            bg=bg_color,
            fg=fg_color,
            activebackground=bg_color,
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=9,
            pady=5,
            cursor="hand2",
            command=command,
        )

    def on_editor_scroll(self, *args):
        self.code_editor.yview(*args)
        self.line_numbers.redraw()

    def on_text_yscroll(self, *args):
        self.scrollbar.set(*args)
        self.line_numbers.redraw()

    def on_editor_key_release(self, event):
        self.highlight_syntax()
        self.line_numbers.redraw()
        self.schedule_auto_analyze(event)

    def highlight_syntax(self):
        content = self.code_editor.get("1.0", "end-1c")
        for tag in ("keyword", "string", "number", "operator", "comment"):
            self.code_editor.tag_remove(tag, "1.0", tk.END)
        for tag, pattern in [
            ("keyword", r"\b(START|END|FUNCTION|RETURN|LET|INT|STR|VOID)\b"),
            ("number", r"\b\d+\b"),
            ("operator", r"(->|=)"),
            ("string", r'"[^"\n]*"'),
            ("comment", r"//[^\n]*"),
        ]:
            for match in re.finditer(pattern, content):
                self.code_editor.tag_add(tag, f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

    def schedule_auto_analyze(self, event=None):
        if event and event.keysym in {"Up", "Down", "Left", "Right", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock"}:
            return
        if self.analyze_after_id is not None:
            self.root.after_cancel(self.analyze_after_id)
        self.analyze_after_id = self.root.after(350, self._run_debounced_analysis)

    def _run_debounced_analysis(self):
        self.analyze_after_id = None
        self.analyze_code()

    def display_trace(self, title, steps, is_error=False):
        self.last_trace_is_error = is_error
        t = self.THEMES[self.current_theme]
        color = t["error_header"] if is_error else t["trace_fg"]
        self.trace_header.config(text=f"DFA State Transition Trace — {title}", fg=color)
        self.trace_box.config(state=tk.NORMAL, fg=color)
        self.trace_box.delete("1.0", tk.END)
        for i, step in enumerate(steps, 1):
            self.trace_box.insert(tk.END, f"Step {i}: {step}\n")
        self.trace_box.config(state=tk.DISABLED)

    def on_token_select(self, event):
        sel = self.token_tree.selection()
        if sel:
            self.error_tree.selection_remove(self.error_tree.selection())
            tok = self.current_tokens[int(self.token_tree.item(sel[0])["values"][0]) - 1]
            self.display_trace(f"Token '{tok.lexeme}' ({tok.type})", tok.trace, False)

    def on_error_select(self, event):
        sel = self.error_tree.selection()
        if sel:
            self.token_tree.selection_remove(self.token_tree.selection())
            err = self.current_errors[int(self.error_tree.item(sel[0])["values"][0]) - 1]
            self.display_trace(f"Error '{err.lexeme}'", err.trace, True)
            err_pos = f"{err.line}.{err.column - 1}"
            self.code_editor.mark_set(tk.INSERT, err_pos)
            self.code_editor.see(err_pos)
            self.line_numbers.redraw()

    def analyze_code(self):
        lexer = MiniLangLexer(self.code_editor.get("1.0", tk.END))
        self.current_tokens, self.current_errors = lexer.tokenize()
        for row in self.token_tree.get_children():
            self.token_tree.delete(row)
        for row in self.error_tree.get_children():
            self.error_tree.delete(row)
        self.code_editor.tag_remove("lexical_error", "1.0", tk.END)

        for idx, tok in enumerate(self.current_tokens, 1):
            self.token_tree.insert("", tk.END, values=(idx, tok.line, tok.column, tok.lexeme, tok.type), tags=(tok.type,))
        for idx, err in enumerate(self.current_errors, 1):
            self.error_tree.insert("", tk.END, values=(idx, err.line, err.column, err.lexeme, err.message), tags=("ERROR",))
            start_col = err.column - 1
            self.code_editor.tag_add("lexical_error", f"{err.line}.{start_col}", f"{err.line}.{start_col + len(err.lexeme)}")

        self.token_header.config(text=f"Recognized Tokens ({len(self.current_tokens)}) — Click any row to inspect DFA trace")
        self.error_header.config(text=f"Lexical Errors ({len(self.current_errors)}) — Click any row to inspect error path & jump to line")

        if self.current_tokens:
            first_id = self.token_tree.get_children()[0]
            self.token_tree.selection_set(first_id)
            self.on_token_select(None)
        elif self.current_errors:
            first_err = self.error_tree.get_children()[0]
            self.error_tree.selection_set(first_err)
            self.on_error_select(None)
        else:
            self.display_trace("None", ["No tokens or errors to trace."])
        self.status_var.set(f"Analysis complete: {len(self.current_tokens)} valid tokens, {len(self.current_errors)} lexical errors.")

    def export_results(self):
        if not self.current_tokens and not self.current_errors:
            messagebox.showwarning("Nothing to Export", "Please analyze some MiniLang code first.")
            return
        file_path = filedialog.asksaveasfilename(title="Export Lexical Analysis Results", defaultextension=".csv", filetypes=[("CSV Spreadsheet", "*.csv"), ("Formatted Text Report", "*.txt")])
        if not file_path:
            return
        try:
            if file_path.endswith(".csv"):
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Status", "Line", "Column", "Lexeme", "Token Category / Error Message", "DFA State Trace"])
                    for tok in self.current_tokens:
                        writer.writerow(["VALID", tok.line, tok.column, tok.lexeme, tok.type, " | ".join(tok.trace)])
                    for err in self.current_errors:
                        writer.writerow(["ERROR", err.line, err.column, err.lexeme, err.message, " | ".join(err.trace)])
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("MINILANG LEXICAL ANALYZER REPORT (CS302)\n" + "=" * 55 + "\n\n")
                    for tok in self.current_tokens:
                        f.write(f"[Line {tok.line}, Col {tok.column}] {tok.type:<15} : {tok.lexeme}\n")
                    f.write("\nLEXICAL ERRORS:\n" + "-" * 55 + "\n")
                    for err in self.current_errors:
                        f.write(f"[Line {err.line}, Col {err.column}] {err.message}: '{err.lexeme}'\n")
            self.status_var.set(f"Exported results to {file_path}")
            messagebox.showinfo("Export Successful", f"Results saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export file:\n{e}")

    def load_sample(self, text):
        if self.analyze_after_id is not None:
            self.root.after_cancel(self.analyze_after_id)
            self.analyze_after_id = None
        self.code_editor.delete("1.0", tk.END)
        self.code_editor.insert("1.0", text)
        self.highlight_syntax()
        self.analyze_code()
        self.line_numbers.redraw()

    def open_file(self):
        path = filedialog.askopenfilename(title="Open MiniLang Source File", filetypes=[("MiniLang Files", "*.minilang *.txt"), ("All Files", "*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.load_sample(f.read())
                self.status_var.set(f"Loaded file: {path}")
            except Exception as e:
                messagebox.showerror("File Error", f"Could not read file:\n{e}")

    def clear_all(self):
        if self.analyze_after_id is not None:
            self.root.after_cancel(self.analyze_after_id)
            self.analyze_after_id = None
        self.code_editor.delete("1.0", tk.END)
        self.code_editor.tag_remove("lexical_error", "1.0", tk.END)
        self.current_tokens = []
        self.current_errors = []
        for row in self.token_tree.get_children():
            self.token_tree.delete(row)
        for row in self.error_tree.get_children():
            self.error_tree.delete(row)
        self.display_trace("None", [])
        self.token_header.config(text="Recognized Tokens (0)")
        self.error_header.config(text="Lexical Errors (0)")
        self.line_numbers.redraw()
        self.status_var.set("Cleared.")


if __name__ == "__main__":
    root = tk.Tk()
    MiniLangGUI(root)
    root.mainloop()