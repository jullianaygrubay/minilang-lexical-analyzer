import tkinter as tk


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


if __name__ == "__main__":
    root = tk.Tk()
    MiniLangGUI(root)
    root.mainloop()