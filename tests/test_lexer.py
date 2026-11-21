from pathlib import Path
from lexer import MiniLangLexer


def test_keywords_and_identifiers():
    code = "START FUNCTION greet(student: STR, score: INT) -> VOID { LET x = 10; RETURN; } END"
    tokens, errors = MiniLangLexer(code).tokenize()

    assert errors == []
    token_pairs = [(t.type, t.lexeme) for t in tokens]
    assert ("KEYWORD", "START") in token_pairs
    assert ("KEYWORD", "FUNCTION") in token_pairs
    assert ("IDENTIFIER", "greet") in token_pairs
    assert ("KEYWORD", "STR") in token_pairs
    assert ("KEYWORD", "INT") in token_pairs
    assert ("RETURN_ARROW", "->") in token_pairs
    assert ("KEYWORD", "VOID") in token_pairs
    assert ("KEYWORD", "LET") in token_pairs
    assert ("ASSIGN_OP", "=") in token_pairs
    assert ("INT_LITERAL", "10") in token_pairs
    assert ("KEYWORD", "RETURN") in token_pairs
    assert ("KEYWORD", "END") in token_pairs


def test_string_literal_and_comment_skipping():
    code = """START
        // This comment should be ignored
        display("Hello CS302", 95);
    END"""
    tokens, errors = MiniLangLexer(code).tokenize()

    assert errors == []
    lexemes = [t.lexeme for t in tokens]
    assert '"Hello CS302"' in lexemes
    assert "// This comment should be ignored" not in lexemes


def test_line_and_column_positions():
    code = "START\n    LET score = 100;\nEND"
    tokens, errors = MiniLangLexer(code).tokenize()

    assert errors == []
    by_lexeme = {t.lexeme: (t.line, t.column) for t in tokens}
    assert by_lexeme["START"] == (1, 1)
    assert by_lexeme["LET"] == (2, 5)
    assert by_lexeme["score"] == (2, 9)
    assert by_lexeme["100"] == (2, 17)
    assert by_lexeme["END"] == (3, 1)


def test_dfa_trace_recorded_for_tokens():
    code = 'greet("Alex", 95);'
    tokens, errors = MiniLangLexer(code).tokenize()

    assert errors == []
    for tok in tokens:
        assert len(tok.trace) > 0
        assert any("q0" in step for step in tok.trace)


def test_lexical_errors_and_recovery():
    code = """START
    123func("Ana");
    display("Unclosed string);
    LET gpa = 98.75;
    FUNCTION bad(x: INT) - VOID {
        / stray slash
        LET y = 10 @ 5;
    }
END"""
    tokens, errors = MiniLangLexer(code).tokenize()

    assert len(errors) >= 6
    for err in errors:
        assert len(err.trace) > 0
        assert any("qe" in step for step in err.trace)

    valid_lexemes = [t.lexeme for t in tokens]
    assert "START" in valid_lexemes
    assert "FUNCTION" in valid_lexemes
    assert "END" in valid_lexemes


def test_valid_demo_sample_file():
    sample_path = Path(__file__).resolve().parent.parent / "samples" / "valid_demo.minilang"
    source = sample_path.read_text(encoding="utf-8")
    tokens, errors = MiniLangLexer(source).tokenize()

    assert errors == []
    assert len(tokens) > 20


def test_error_demo_sample_file():
    sample_path = Path(__file__).resolve().parent.parent / "samples" / "error_demo.minilang"
    source = sample_path.read_text(encoding="utf-8")
    tokens, errors = MiniLangLexer(source).tokenize()

    assert len(errors) == 7
    assert any(t.lexeme == "END" for t in tokens)