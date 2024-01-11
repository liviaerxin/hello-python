import ply.yacc as yacc
from lexer import tokens


class Node:
    def __init__(self, op, left=None, right=None, val=None) -> None:
        self.op = op
        self.left = left
        self.right = right
        self.val = val

    @property
    def is_leaf(self):
        if self.left is None and self.right is None:
            return True
        return False

    @property
    def is_internal(self):
        return not self.is_leaf


precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
)


def p_expression_binop(p):
    """
    expression  : expression PLUS expression
                | expression MINUS expression
                | expression TIMES expression
                | expression DIVIDE expression
    """
    if p[2] == "+":
        p[0] = Node("plus", left=p[1], right=p[3])
    if p[2] == "-":
        p[0] = Node("minus", left=p[1], right=p[3])
    if p[2] == "*":
        p[0] = Node("times", left=p[1], right=p[3])
    if p[2] == "/":
        p[0] = Node("divide", left=p[1], right=p[3])


def p_expression_group(p):
    """
    expression : LPAREN expression RPAREN
    """
    p[0] = p[2]


def p_expression_number(p):
    """
    expression : NUMBER
    """
    p[0] = Node("number", val=p[1])


def traverse_ast(ast):
    if ast.is_leaf:
        return f"[{ast.op} {ast.val}]"
    else:
        left = traverse_ast(ast.left)
        right = traverse_ast(ast.right)
        return f"[{ast.op} {left} {right}]"


def interpret_ast(ast):
    if ast.is_leaf:
        if ast.op == "number":
            return ast.val
    else:
        left = interpret_ast(ast.left)
        right = interpret_ast(ast.right)

        if ast.op == "plus":
            return left + right
        elif ast.op == "minus":
            return left - right
        elif ast.op == "times":
            return left * right
        elif ast.op == "divide":
            return left / right

# nasm
registers = {"r8": True, "r9": True, "r10": True, "r11": True}

def get_register():
    for k, v in registers.items():
        if v:
            registers[k] = False
            return k
    return None

def free_register(k):
    registers[k] = True
    
def cg_load(val):
    reg = get_register()
    print(f"\tmov\t{reg}, {val}")
    return reg

def cg_plus(r1, r2):
    print(f"\tadd\t{r2}, {r1}")
    free_register(r1)
    return r2
    
def cg_minus(r1, r2):
    print(f"\tsub\t{r1}, {r2}")
    free_register(r2)
    return r1

def cg_times(r1, r2):
    print(f"\timul\t{r2}, {r1}")
    free_register(r1)
    return r2

def cg_divide(r1, r2):
    print(f"\tmov\trax, {r1}")
    print(f"\tcqo")
    print(f"\tidvi\t{r2}")
    print(f"\tmov\t{r1}, rax")

    free_register(r2)
    return r1

def gen_ast(ast):    
    if ast.is_leaf:
        if ast.op == "number":
            return cg_load(ast.val)
    else:
        left_val = gen_ast(ast.left)
        right_val = gen_ast(ast.right)

        if ast.op == "plus":
            return cg_plus(left_val, right_val)
        elif ast.op == "minus":
            return cg_minus(left_val, right_val)
        elif ast.op == "times":
            return cg_times(left_val, right_val)
        elif ast.op == "divide":
            return cg_divide(left_val, right_val)
        
# Build the parser
parser = yacc.yacc()

input_code = """
1+2*3
"""
print(f"{input_code}")
ast = parser.parse(input_code)
print(traverse_ast(ast))
print(interpret_ast(ast))

input_code = """
(1+2)*3
"""
print(f"{input_code}")
ast = parser.parse(input_code)
print(traverse_ast(ast))
print(interpret_ast(ast))

input_code = """
3*5-1
"""
print(f"{input_code}")
ast = parser.parse(input_code)
print(traverse_ast(ast))
print(interpret_ast(ast))
print(gen_ast(ast))