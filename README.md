# MiniLang Lexical Analyzer & DFA Tracer

[![Run MiniLang Lexer Tests](https://github.com/jullianaygrubay/minilang-lexical-analyzer/actions/workflows/tests.yml/badge.svg)](https://github.com/jullianaygrubay/minilang-lexical-analyzer/actions/workflows/tests.yml)

An interactive **Deterministic Finite Automaton (DFA)** lexical analyzer and desktop IDE built with Python and Tkinter for **MiniLang**.

## Features
- **Explicit DFA Engine (`lexer.py`):** Simulates states `q0`–`q8` and error sink `qe` with step-by-step transition logging.
- **Interactive Desktop IDE (`minilang_gui.py`):** Synchronized line numbers, live syntax highlighting, debounced auto-analysis, inline red error underlines with click-to-jump, and CSV/TXT report export.

## Quick Start
```bash
python minilang_gui.py
```

## Sample Files

- samples/valid_demo.minilang — Valid MiniLang functions, typed parameters, return arrows, and nested calls.

- samples/error_demo.minilang — Intentional lexical edge cases for testing DFA error sink (qe) recovery.