# src/lexer_state.py
from tokens import Token, KEYWORDS, TYPES, PUNCT, OPERATORS, SINGLE_OPS, is_identifier_start, is_identifier_part

class LexerState:
    DEFAULT = 0
    IDENT = 1
    NUMBER = 2
    STRING = 3
    SLASH = 4  # maybe comment or operator
    LINE_COMMENT = 5
    BLOCK_COMMENT = 6

def lex(code: str):
    i = 0
    line = 1
    col = 1
    n = len(code)

    def peek(k=0):
        j = i + k
        return code[j] if j < n else ""

    def advance():
        nonlocal i, line, col
        ch = code[i] if i < n else ""
        i += 1
        if ch == "\n":
            line += 1
            col = 1
        else:
            col += 1
        return ch

    def make_token(type_, value=None, length=0):
        # length isn't tracked per token here; we rely on current line/col being correct at token start
        return Token(type_, value, line, col)

    # Precompute operator trie (longest match first)
    op_list = [op for op, _ in sorted(OPERATORS, key=lambda x: -len(x[0]))]
    op_map = dict(OPERATORS)

    while i < n:
        ch = peek()
        # Whitespace
        if ch.isspace():
            advance()
            continue

        # Punctuations
        if ch in PUNCT:
            t = PUNCT[ch]
            advance()
            yield Token(t, None, line, col)
            continue

        # Handle comments first
        if ch == '/' and (i+1) < n and code[i+1] == '/':
            # // line comment
            advance(); advance()
            while i < n and peek() != '\n':
                advance()
            continue
        if ch == '/' and (i+1) < n and code[i+1] == '*':
            # /* block comment */
            advance(); advance()
            while i < n and not (peek() == '*' and (i+1) < n and code[i+1] == '/'):
                advance()
            if i >= n:
                raise SyntaxError(f"Unterminated block comment at {line}:{col}")
            advance(); advance()
            continue

        # Multi-character operators (longest to shortest)
        matched_op = None
        for op in op_list:
            if code.startswith(op, i):
                matched_op = op
                break
        if matched_op:
            tok_type = op_map[matched_op]
            for _ in range(len(matched_op)):
                advance()
            yield Token(tok_type, None, line, col)
            continue

        # Single-char ops
        if ch in SINGLE_OPS:
            t = SINGLE_OPS[ch]
            advance()
            yield Token(t, None, line, col)
            continue

        # String literal
        if ch == '"':
            advance()  # consume opening quote
            buf = []
            while i < n:
                c = advance()
                if c == '"':
                    break
                if c == "\\":
                    esc = advance()
                    if esc == "n":
                        buf.append("\n")
                    elif esc == "t":
                        buf.append("\t")
                    elif esc == "r":
                        buf.append("\r")
                    elif esc == '"':
                        buf.append('"')
                    elif esc == "\\":
                        buf.append("\\")
                    elif esc == "u":
                        # unicode escape \uXXXX
                        hex_digits = "".join(advance() for _ in range(4))
                        try:
                            buf.append(chr(int(hex_digits, 16)))
                        except:
                            raise SyntaxError(f"Invalid unicode escape at {line}:{col}: \\u{hex_digits}")
                    else:
                        # Unknown escape: keep as literal
                        buf.append("\\" + esc)
                else:
                    buf.append(c)
            else:
                raise SyntaxError(f"Unterminated string at {line}:{col}")
            yield Token("STRINGLIT", "".join(buf), line, col)
            continue

        # Number (int or float)
        if ch.isdigit():
            start_line, start_col = line, col
            num_str = []
            while i < n and peek().isdigit():
                num_str.append(advance())
            # include current digit (first)
            if not num_str:
                num_str.append(advance())
            # decimal part
            if peek() == "." and (i+1) < n and code[i+1].isdigit():
                num_str.append(advance())  # dot
                while i < n and peek().isdigit():
                    num_str.append(advance())
                # exponent
                if peek() in "eE":
                    num_str.append(advance())
                    if peek() in "+-":
                        num_str.append(advance())
                    if not peek().isdigit():
                        raise SyntaxError(f"Malformed float exponent at {line}:{col}")
                    while i < n and peek().isdigit():
                        num_str.append(advance())
                yield Token("FLOATLIT", float("".join(num_str)), start_line, start_col)
            else:
                # if next char is a letter or underscore, invalid identifier like 123abc
                if is_identifier_start(peek()):
                    bad = [peek()]
                    advance()
                    while is_identifier_part(peek()):
                        bad.append(advance())
                    raise SyntaxError(f"Invalid identifier starting with number at {start_line}:{start_col}: '{''.join(num_str)+''.join(bad)}'")
                yield Token("INTLIT", int("".join(num_str)), start_line, start_col)
            continue

        # Identifier or keyword/type (supports unicode letters + underscore)
        if is_identifier_start(ch):
            start_line, start_col = line, col
            buf = [advance()]
            while is_identifier_part(peek()):
                buf.append(advance())
            ident = "".join(buf)
            if ident in KEYWORDS:
                t = KEYWORDS[ident]
                if t == "BOOLLIT":
                    val = True if ident == "true" else False
                    yield Token("BOOLLIT", val, start_line, start_col)
                else:
                    yield Token(t, None, start_line, start_col)
            elif ident in TYPES:
                yield Token(TYPES[ident], None, start_line, start_col)
            else:
                yield Token("IDENTIFIER", ident, start_line, start_col)
            continue

        # If we get here, it's an unknown char
        raise SyntaxError(f"Unexpected character at {line}:{col}: '{ch}'")
