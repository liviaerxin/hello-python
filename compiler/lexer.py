import ply.lex as lex

# List of token names. This is always required
tokens = ["ID", "NUMBER", "PLUS", "MINUS", "TIMES", "DIVIDE", "EQUALS", "LPAREN", "RPAREN", "SEMICOLON"]

# Regular expression rules for simple tokens
t_EQUALS = r'\='
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_SEMICOLON = r";"

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

# A regular expression rule with some action code
def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore = " \t"

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

if __name__ == "__main__":
    data = """
    3 + 4 *10
      + -20 *2;
    a = 2;
    """
    lexer.input(data)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
