# Simple Lexer (Two Implementations)

This mini-project contains **two** lexical analyzers for a tiny C-like language:

- `lexer_regex.py`: implemented using Python `re` with a master pattern.
- `lexer_state.py`: implemented **without regex**, using raw string comparisons and a hand-written state machine.

Both support:
- Keywords: `fn`, `return`, `if`, `else`, `for`, `while`
- Types: `int`, `float`, `string`, `bool`
- Literals: integers, floats, booleans (`true`/`false`), and strings with escapes (`\"`, `\\`, `\n`, `\t`, `\r`, `\uXXXX`)
- Operators: `==`, `!=`, `<=`, `>=`, `&&`, `||`, `<<`, `>>`, `++`, `--`, compound assignments, plus single-char ops.
- Punctuation: parentheses `()`, braces `{}`, brackets `[]`, commas, semicolons, dot, colon, question mark.
- Comments: `// line` and `/* block */` (properly skipped)
- **Error** on invalid identifiers that start with a number (e.g., `123abc`).
- **Bonus:** Unicode identifiers (e.g., emojis or non‑Latin letters) and Unicode escapes inside strings.

## Run locally

```bash
python run_all.py
```

Outputs appear in `outputs/` and PNG "screenshots" in `screenshots/`.
