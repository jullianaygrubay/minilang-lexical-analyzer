# MiniLang Lexical Analyzer & DFA Tracer

An interactive **Deterministic Finite Automaton (DFA)** lexical analyzer and desktop IDE built with Python and Tkinter for **MiniLang**.

## Features
- **Explicit DFA Engine (`lexer.py`):** Simulates states `q0`–`q8` and error sink `qe` with step-by-step transition logging.
- **Interactive Desktop IDE (`minilang_gui.py`):** Synchronized line numbers, live syntax highlighting, debounced auto-analysis, inline red error underlines with click-to-jump, and CSV/TXT report export.