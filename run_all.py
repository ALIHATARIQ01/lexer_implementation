# run_all.py
from src.lexer_regex import lex as lex_re
from src.lexer_state import lex as lex_sm

code = open("sample_input.fn", "r", encoding="utf-8").read()

def render(tokens):
    return "[" + ", ".join(repr(t) for t in tokens) + "]"

# Regex version
tokens_re = list(lex_re(code))
open("outputs/regex_tokens.txt", "w", encoding="utf-8").write(render(tokens_re))

# State-machine version
tokens_sm = list(lex_sm(code))
open("outputs/state_tokens.txt", "w", encoding="utf-8").write(render(tokens_sm))
print("Wrote outputs/regex_tokens.txt and outputs/state_tokens.txt")
