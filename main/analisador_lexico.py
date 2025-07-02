import re


token_specification = [
    ('KEYWORD', r'\b(if|else|while|for|return|func|int)\b'), 
    ('NUMBER', r'\b\d+\b'),
    ('ID', r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'),
    ('OP', r'(==|!=|<=|>=|&&|\|\||[+\-*/=<>%])'),
    ('STRING', r'"[^"\n]*"'),
    ('SYMBOL', r'[;(),{}]'),
    ('WHITESPACE', r'\s+'),
    ('UNKNOWN', r'.'),
]

token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)

def analisador_lexico(codigo_fonte):
    tokens = []
    for match in re.finditer(token_regex, codigo_fonte):
        tipo = match.lastgroup
        valor = match.group()
        if tipo == 'WHITESPACE':
            continue
        elif tipo == 'UNKNOWN':
            raise ValueError(f'Erro: Caractere inválido "{valor}"')
        else:
            tokens.append((tipo, valor))
    return tokens
