class Token:
    def __init__(self, token_type, lexeme, line, column, trace=None):
        self.type = token_type
        self.lexeme = lexeme
        self.line = line
        self.column = column
        self.trace = trace or []

    def __repr__(self):
        return f"Token({self.type:<14} | {self.lexeme:<12} | Line {self.line}, Col {self.column})"


class LexicalError:
    def __init__(self, message, lexeme, line, column, trace=None):
        self.message = message
        self.lexeme = lexeme
        self.line = line
        self.column = column
        self.trace = trace or []

    def __repr__(self):
        return f"LexicalError({self.message:<34} | {self.lexeme:<12} | Line {self.line}, Col {self.column})"


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

            # q0 -> q0: Whitespace
            if char in {' ', '\t', '\r', '\n'}:
                self.advance()

            # q0 -> q1: Identifier or Keyword
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

            # q0 -> q3: String Literal
            elif char == '"':
                lexeme, trace = self.advance(), ["q0 --('\"')--> q3"]
                while self.current_char() is not None and self.current_char() not in {'"', '\n'}:
                    ch = self.advance()
                    lexeme += ch
                    trace.append(f"q3 --('{ch}')--> q3")
                if self.current_char() == '"':
                    lexeme += self.advance()
                    trace.append("q3 --('\"')--> q0 [ACCEPT: STRING_LITERAL]")
                    self.tokens.append(Token("STRING_LITERAL", lexeme, start_line, start_col, trace))
                else:
                    trace.append("q3 --(newline/EOF)--> qe [ERROR: Unclosed string]")
                    self.errors.append(LexicalError("Unclosed string literal", lexeme, start_line, start_col, trace))

            # q0 -> q4: Assignment Operator (=)
            elif char == '=':
                lexeme = self.advance()
                self.tokens.append(Token("ASSIGN_OP", lexeme, start_line, start_col, ["q0 --('=')--> q4", "q4 --> q0 [ACCEPT: ASSIGN_OP]"]))

            # q0 -> q5: Return Arrow (->)
            elif char == '-':
                lexeme, trace = self.advance(), ["q0 --('-')--> q5"]
                if self.current_char() == '>':
                    lexeme += self.advance()
                    trace.append("q5 --('>')--> q0 [ACCEPT: RETURN_ARROW]")
                    self.tokens.append(Token("RETURN_ARROW", lexeme, start_line, start_col, trace))
                else:
                    nxt = self.current_char() if self.current_char() else "EOF"
                    trace.append(f"q5 --('{nxt}')--> qe [ERROR: Expected '>']")
                    self.errors.append(LexicalError("Invalid operator (expected '->')", lexeme, start_line, start_col, trace))

            # q0 -> q6 -> q8: Single-line Comment (//)
            elif char == '/':
                lexeme, trace = self.advance(), ["q0 --('/')--> q6"]
                if self.current_char() == '/':
                    self.advance()
                    trace.append("q6 --('/')--> q8 [COMMENT START]")
                    while self.current_char() is not None and self.current_char() != '\n':
                        self.advance()
                    trace.append("q8 --(newline)--> q0 [COMMENT END]")
                else:
                    nxt = self.current_char() if self.current_char() else "EOF"
                    trace.append(f"q6 --('{nxt}')--> qe [ERROR: Expected '/']")
                    self.errors.append(LexicalError("Invalid operator (expected '//')", lexeme, start_line, start_col, trace))

            # q0 -> q7: Delimiters
            elif char in self.DELIMITERS:
                lexeme = self.advance()
                self.tokens.append(Token("DELIMITER", lexeme, start_line, start_col, [f"q0 --('{lexeme}')--> q7", "q7 --> q0 [ACCEPT: DELIMITER]"]))

            # q0 -> qe: Unrecognized Symbol
            else:
                lexeme = self.advance()
                self.errors.append(LexicalError("Unrecognized symbol", lexeme, start_line, start_col, [f"q0 --('{lexeme}')--> qe [ERROR: Unrecognized symbol]"]))

        return self.tokens, self.errors