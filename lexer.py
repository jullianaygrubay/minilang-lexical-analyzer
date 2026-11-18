class Token:
    def __init__(self, token_type, lexeme, line, column, trace=None):
        self.type = token_type
        self.lexeme = lexeme
        self.line = line
        self.column = column
        self.trace = trace or []

    def __repr__(self):
        return f"Token({self.type:<12} | {self.lexeme:<10} | Line {self.line}, Col {self.column})"


class LexicalError:
    def __init__(self, message, lexeme, line, column, trace=None):
        self.message = message
        self.lexeme = lexeme
        self.line = line
        self.column = column
        self.trace = trace or []

    def __repr__(self):
        return f"LexicalError({self.message:<34} | {self.lexeme:<10} | Line {self.line}, Col {self.column})"


class MiniLangLexer:
    KEYWORDS = {"START", "END", "FUNCTION", "RETURN", "LET", "INT", "STR", "VOID"}
    DELIMITERS = {'(', ')', '{', '}', ',', ':', ';'}

    def __init__(self, source_code):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.errors = []

    def current_char(self):
        return self.source[self.pos] if self.pos < len(self.source) else None

    def advance(self):
        char = self.current_char()
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def tokenize(self):
        while self.current_char() is not None:
            char = self.current_char()
            start_line, start_col = self.line, self.column

            if char in {' ', '\t', '\r', '\n'}:
                self.advance()

            elif char.isalpha() or char == '_':
                first = self.advance()
                lexeme = first
                trace = [f"q0 --('{first}')--> q1"]
                while self.current_char() is not None and (self.current_char().isalnum() or self.current_char() == '_'):
                    ch = self.advance()
                    lexeme += ch
                    trace.append(f"q1 --('{ch}')--> q1")
                token_type = "KEYWORD" if lexeme in self.KEYWORDS else "IDENTIFIER"
                trace.append(f"q1 --(delimiter/space)--> q0 [ACCEPT: {token_type}]")
                self.tokens.append(Token(token_type, lexeme, start_line, start_col, trace))

            # q0 -> q2: Integer Literal (or malformed -> qe)
            elif char.isdigit():
                first = self.advance()
                lexeme, trace, is_malformed = first, [f"q0 --('{first}')--> q2"], False
                while self.current_char() is not None and (self.current_char().isalnum() or self.current_char() in {'_', '.'}):
                    ch = self.advance()
                    lexeme += ch
                    if not ch.isdigit():
                        is_malformed = True
                        trace.append(f"q2 --('{ch}')--> qe [ERROR: Invalid char in integer]")
                    else:
                        trace.append(f"qe --('{ch}')--> qe" if is_malformed else f"q2 --('{ch}')--> q2")
                if is_malformed:
                    self.errors.append(LexicalError("Invalid identifier / malformed number", lexeme, start_line, start_col, trace))
                else:
                    trace.append("q2 --(delimiter/space)--> q0 [ACCEPT: INT_LITERAL]")
                    self.tokens.append(Token("INT_LITERAL", lexeme, start_line, start_col, trace))

            elif char in self.DELIMITERS:
                lexeme = self.advance()
                self.tokens.append(Token("DELIMITER", lexeme, start_line, start_col, [f"q0 --('{lexeme}')--> q7", "q7 --> q0 [ACCEPT: DELIMITER]"]))

            else:
                self.advance()

        return self.tokens, self.errors


if __name__ == "__main__":
    tokens, errors = MiniLangLexer("START 100 123abc END").tokenize()
    print("Tokens:", tokens)
    print("Errors:", errors)
