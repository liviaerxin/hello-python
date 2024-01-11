import ply.lex as lex
import ply.yacc as yacc

# Lexer
tokens = ('ID', 'NUMBER', 'PRINT', 'EQUALS', 'SEMICOLON')

t_EQUALS = r'='
t_SEMICOLON = r';'
t_PRINT = r'print'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = 'ID'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t\n'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# Parser
def p_statement_assign(p):
    'statement : ID EQUALS NUMBER SEMICOLON'
    p[0] = ('assign', p[1], p[3])

def p_statement_print(p):
    'statement : PRINT LPAREN ID RPAREN SEMICOLON'
    p[0] = ('print', p[3])

def p_error(p):
    print(f"Syntax error at '{p.value}'")

parser = yacc.yacc()

# Code Generator
def generate_code(ast):
    if ast[0] == 'assign':
        return f"mov {ast[1]}, {ast[2]}"
    elif ast[0] == 'print':
        return f"print {ast[1]}"
    else:
        return ''

# Example C2 program
c2_program = '''
a = 42;
print(a);
'''

# Lex and parse the C2 program
lexer.input(c2_program)
ast = parser.parse(c2_program, lexer=lexer)

# Generate assembly code
assembly_code = generate_code(ast)

print(f"Generated Assembly Code:\n{assembly_code}")
