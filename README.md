# MiniLang Lexical Analyzer & DFA Tracer

[![Run MiniLang Lexer Tests](https://github.com/jullianaygrubay/minilang-lexical-analyzer/actions/workflows/tests.yml/badge.svg)](https://github.com/jullianaygrubay/minilang-lexical-analyzer/actions/workflows/tests.yml)

An explicit **Deterministic Finite Automaton (DFA)** lexical analyzer and interactive desktop IDE built with Python and Tkinter.

## Features

- **Explicit DFA Scanner (`lexer.py`):** Scans MiniLang source code across states `q0`–`q8` with panic-mode error recovery (`qe`) and line/column position tracking.
- **Interactive Desktop IDE (`minilang_gui.py`):** Features a code editor with synchronized line numbers, live syntax highlighting, debounced auto-analysis, inline error jump-to-line, Light/Dark theme switching (`Ctrl+T`), sample program loaders, and token/error inspection.
- **Export & Reporting:** Export lexical analysis results and token tables to CSV or TXT formats.
- **Automated Testing & CI:** Includes a `pytest` unit test suite (`tests/test_lexer.py`) integrated with GitHub Actions.
- **Standalone Windows Build:** Can be packaged into a single executable (`MiniLangAnalyzer.exe`) via PyInstaller without requiring Python on the target machine.

## Screenshots

| Dark Mode — Valid Program (`Ctrl+T`) | Light Mode — Lexical Error Recovery (`Ctrl+T`) |
| :---: | :---: |
| ![Dark Mode Valid Program](assets/screenshots/ide-valid-dark.png) | ![Light Mode Lexical Error View](assets/screenshots/ide-errors-light.png) |
| *Live syntax highlighting, DFA trace & token table* | *Panic-mode error detection (`qe`) and diagnostics* |

## DFA State Transition Diagram

```mermaid
flowchart LR
    start((▶ Start)) --> q0((q0))

    %% Identifiers & Keywords
    q0 -- "🔤 letter / _" --> q1(((q1<br/>🏷️ ID / KW)))
    q1 -- "🔤 letter / digit / _" --> q1

    %% Integer Literals
    q0 -- "🔢 digit" --> q2(((q2<br/>#️⃣ INT)))
    q2 -- "🔢 digit" --> q2
    q2 -- "❌ . or letter" --> qe(((qe<br/>⚠️ ERROR)))

    %% String Literals
    q0 -- "💬 #quot;" --> q3((q3))
    q3 -- "📝 any char ≠ #quot;, \n" --> q3
    q3 -- "💬 #quot;" --> q4(((q4<br/>📜 STR)))
    q3 -- "❌ \n or EOF" --> qe

    %% Assignment Operator
    q0 -- "🟰 =" --> q5(((q5<br/>⚙️ ASSIGN)))

    %% Return Arrow
    q0 -- "➖ -" --> q6((q6))
    q6 -- "➡️ >" --> q7(((q7<br/>↪️ ARROW)))
    q6 -- "❌ other" --> qe

    %% Delimiters
    q0 -- "🔣 ( ) { } : ; ," --> q8(((q8<br/>🧩 DELIM)))

    %% Unrecognized Symbol
    q0 -- "❌ other symbol" --> qe

    %% Styling
    style q0 fill:#282a36,stroke:#bd93f9,stroke-width:3px,color:#f8f8f2
    style q3 fill:#282a36,stroke:#8be9fd,stroke-width:2px,color:#f8f8f2
    style q6 fill:#282a36,stroke:#8be9fd,stroke-width:2px,color:#f8f8f2
    style q1 fill:#1e3a2f,stroke:#50fa7b,stroke-width:3px,color:#f8f8f2
    style q2 fill:#1e3a2f,stroke:#50fa7b,stroke-width:3px,color:#f8f8f2
    style q4 fill:#1e3a2f,stroke:#50fa7b,stroke-width:3px,color:#f8f8f2
    style q5 fill:#1e3a2f,stroke:#50fa7b,stroke-width:3px,color:#f8f8f2
    style q7 fill:#1e3a2f,stroke:#50fa7b,stroke-width:3px,color:#f8f8f2
    style q8 fill:#1e3a2f,stroke:#50fa7b,stroke-width:3px,color:#f8f8f2
    style qe fill:#441c24,stroke:#ff5555,stroke-width:3px,color:#f8f8f2
```

## Lexical Token Specification

| Token Category | Accepting State | Pattern / Lexemes | Examples |
| :--- | :---: | :--- | :--- |
| **KEYWORD** | `q1` | `START`, `END`, `FUNCTION`, `LET`, `RETURN`, `IF`, `ELSE`, `WHILE`, `PRINT`, `display` | `START`, `FUNCTION`, `LET` |
| **DATA_TYPE** | `q1` | `INT`, `STR`, `FLOAT`, `BOOL`, `VOID` | `INT`, `STR`, `VOID` |
| **IDENTIFIER** | `q1` | `[a-zA-Z_][a-zA-Z0-9_]*` (excluding keywords & types) | `greet`, `score`, `check_grade` |
| **INT_LITERAL** | `q2` | `[0-9]+` | `0`, `95`, `100` |
| **STRING_LITERAL** | `q4` | `"[^"\n]*"` | `"Alex"`, `"CS302"` |
| **ASSIGN_OP** | `q5` | `=` | `=` |
| **RETURN_ARROW** | `q7` | `->` | `->` |
| **DELIMITER** | `q8` | `(`, `)`, `{`, `}`, `;`, `,`, `:` | `(`, `)`, `{`, `;`, `:` |
| **COMMENT** *(Ignored)* | `q6` | `//[^\n]*` | `// Define a function` |
| **LEXICAL_ERROR** | `qe` | Unclosed strings, invalid symbols, or malformed identifiers (e.g. `123func`, `95.50`, `+`) | `123func`, `"Unclosed string` |

## Quick Start
```bash
python minilang_gui.py
```

## Sample Files
- `samples/valid_demo.minilang` — Valid MiniLang functions, typed parameters, return arrows, and nested calls.
- `samples/error_demo.minilang` — Intentional lexical edge cases for testing DFA error sink (`qe`) recovery.