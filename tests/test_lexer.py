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