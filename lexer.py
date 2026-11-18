class Token:
    def __init__(self, token_type, lexeme, line, column, trace=None):
        self.type = token_type
        self.lexeme = lexeme
        self.line = line
        self.column = column
        self.trace = trace or []

    def __repr__(self):
        return f"Token({self.type} | {self.lexeme} | L{self.line}:C{self.column})"


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


if __name__ == "__main__":
    scanner = MiniLangLexer("START")
    print("First char:", scanner.advance())
