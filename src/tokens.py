# tokens.py
from dataclasses import dataclass
import unicodedata

@dataclass(frozen=True)
class Token:
    type: str
    value: object = None
    line: int = 0
    col: int = 0

    def __repr__(self):
        if self.value is None:
            return f"T_{self.type}"
        # For strings and identifiers, show as TYPE("value"); otherwise TYPE(value)
        if isinstance(self.value, str):
            safe = self.value.replace("\\n", "\\\\n").replace("\\t", "\\\\t").replace('"', '\\"')
            return f"T_{self.type}(\"{safe}\")"
        return f"T_{self.type}({self.value})"

KEYWORDS = {
    "fn": "FUNCTION",
    "return": "RETURN",
    "if": "IF",
    "else": "ELSE",
    "for": "FOR",
    "while": "WHILE",
    "true": "BOOLLIT",
    "false": "BOOLLIT",
}

TYPES = {
    "int": "INT",
    "float": "FLOAT",
    "string": "STRING",
    "bool": "BOOL",
}

PUNCT = {
    "(": "PARENL",
    ")": "PARENR",
    "{": "BRACEL",
    "}": "BRACER",
    "[": "BRACKETL",
    "]": "BRACKETR",
    ",": "COMMA",
    ";": "SEMICOLON",
}

# Multi-character operators first (longest match wins)
OPERATORS = [
    ("==", "EQUALSOP"),
    ("!=", "NOTEQUALSOP"),
    ("<=", "LEOP"),
    (">=", "GEOP"),
    ("&&", "ANDOP"),
    ("||", "OROP"),
    ("<<", "LSHIFT"),
    (">>", "RSHIFT"),
    ("++", "INCR"),
    ("--", "DECR"),
    ("+=", "PLUSEQ"),
    ("-=", "MINUSEQ"),
    ("*=", "STAREQ"),
    ("/=", "SLASHEQ"),
    ("%=", "MODEQ"),
    ("&=", "ANDEQ"),
    ("|=", "OREQ"),
    ("^=", "XOREQ"),
]

SINGLE_OPS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "%": "PERCENT",
    "=": "ASSIGNOP",
    "<": "LT",
    ">": "GT",
    "!": "BANG",
    "&": "AMP",
    "|": "PIPE",
    "^": "CARET",
    "~": "TILDE",
    "?": "QMARK",
    ":": "COLON",
    ".": "DOT",
}

def is_unicode_letter(ch: str) -> bool:
    # True for categories starting with 'L' (Letter)
    return len(ch) == 1 and unicodedata.category(ch).startswith("L")

def is_identifier_start(ch: str) -> bool:
    # underscore or any unicode letter
    return ch == "_" or is_unicode_letter(ch)

def is_identifier_part(ch: str) -> bool:
    # underscore, unicode letter or digit
    return ch == "_" or is_unicode_letter(ch) or ch.isdigit()
