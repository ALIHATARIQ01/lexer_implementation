# src/lexer_regex.py
import re
from tokens import Token, KEYWORDS, TYPES, PUNCT, OPERATORS, SINGLE_OPS

# Build regex pattern for tokens. Use named groups.
# We allow unicode identifiers via Python's \w augmented with explicit range by using a custom pattern:
# Start: underscore or any unicode letter (via \p{L} which Python's 're' lacks), so we fallback to a conservative pattern and post-validate.
IDENT_PATTERN = r"[A-Za-z_\u00C0-\uFFFF][A-Za-z0-9_\u00C0-\uFFFF]*"

WHITESPACE = r"(?P<WS>\s+)"
LINE_COMMENT = r"(?P<LC>//[^\n]*)"
BLOCK_COMMENT = r"(?P<BC>/\*.*?\*/)"
INT = r"(?P<INTLIT>\d+)"
FLOAT = r"(?P<FLOATLIT>\d+\.\d+([eE][+-]?\d+)?)"
# String with escapes \" \\ \n \t \r and unicode escapes like \uXXXX (we'll unescape later)
STRING = r"(?P<STRINGLIT>\"(?:\\.|[^\"\\])*\")"

# Operators (longest first)
OPS = "|".join(re.escape(op) for op, _ in sorted(OPERATORS, key=lambda x: -len(x[0])))
SOPS = "|".join(re.escape(k) for k in SINGLE_OPS.keys())
PUN = "|".join(re.escape(k) for k in PUNCT.keys())

MASTER = re.compile(
    "|".join([
        FLOAT,        # float before int
        INT,
        STRING,
        LINE_COMMENT,
        BLOCK_COMMENT,
        r"(?P<OP>(" + OPS + "))",
        r"(?P<SOP>(" + SOPS + "))",
        r"(?P<PUN>(" + PUN + "))",
        r"(?P<IDENT>" + IDENT_PATTERN + ")",
        WHITESPACE,
    ]),
    re.DOTALL | re.UNICODE
)

def unescape_string(s: str) -> str:
    # Remove surrounding quotes then interpret escapes
    body = s[1:-1]
    # Handle common escapes
    def repl(m):
        esc = m.group(1)
        if esc == 'n': return '\n'
        if esc == 't': return '\t'
        if esc == 'r': return '\r'
        if esc == '"': return '"'
        if esc == '\\': return '\\'
        if esc.startswith('u') and len(esc) == 5:
            try:
                return chr(int(esc[1:], 16))
            except:
                return '\\' + esc
        return '\\' + esc
    return re.sub(r'\\(u[0-9a-fA-F]{4}|.|$)', repl, body)

def lex(code: str):
    pos = 0
    line = 1
    col = 1
    while pos < len(code):
        m = MASTER.match(code, pos)
        if not m:
            snippet = code[pos:pos+20].replace("\n", "\\n")
            raise SyntaxError(f"Unexpected character at {line}:{col} near '{snippet}'")
        text = m.group(0)
        kind = m.lastgroup
        if kind == "WS":
            # update location
            lines = text.splitlines(True)
            for seg in lines:
                if seg.endswith(("\n", "\r")):
                    line += 1
                    col = 1
                else:
                    col += len(seg)
        elif kind in ("LC", "BC"):
            # comments ignored but update line/col appropriately
            lines = text.splitlines(True)
            for seg in lines:
                if seg.endswith(("\n", "\r")):
                    line += 1
                    col = 1
                else:
                    col += len(seg)
        elif kind == "PUN":
            yield Token(PUNCT[text], None, line, col)
            col += len(text)
        elif kind == "OP":
            # map to operator token
            tok_type = dict(OPERATORS)[text]
            yield Token(tok_type, None, line, col)
            col += len(text)
        elif kind == "SOP":
            yield Token(SINGLE_OPS[text], None, line, col)
            col += len(text)
        elif kind == "STRINGLIT":
            yield Token("STRINGLIT", unescape_string(text), line, col)
            col += len(text)
        elif kind == "FLOATLIT":
            yield Token("FLOATLIT", float(text), line, col)
            col += len(text)
        elif kind == "INTLIT":
            yield Token("INTLIT", int(text), line, col)
            col += len(text)
        elif kind == "IDENT":
            # Distinguish keywords/types/identifiers
            if text in KEYWORDS:
                t = KEYWORDS[text]
                if t == "BOOLLIT":
                    yield Token("BOOLLIT", True if text == "true" else False, line, col)
                else:
                    yield Token(t, None, line, col)
            elif text in TYPES:
                yield Token(TYPES[text], None, line, col)
            else:
                # Validate: cannot start with digit (already ensured by IDENT pattern). Also allow unicode via Python check.
                if not (text[0] == "_" or text[0].isalpha() or ord(text[0]) >= 128):
                    raise SyntaxError(f"Invalid identifier at {line}:{col}: '{text}'")
                yield Token("IDENTIFIER", text, line, col)
            col += len(text)
        else:
            # Shouldn't happen
            col += len(text)
        pos = m.end()
