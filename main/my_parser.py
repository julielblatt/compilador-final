from analisador_lexico import analisador_lexico
from ast1 import (
    ProgramNode, AssignNode, ReturnNode,
    BinOpNode, NumberNode, VariableNode,
    FuncDeclNode, FuncCallNode,
    IfNode, WhileNode, ForNode,
    ASTNode, UnaryOpNode,
)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def token_atual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', '')

    def consumir(self, tipo_esperado):
        tipo, valor = self.token_atual()
        if tipo == tipo_esperado:
            self.pos += 1
            return valor
        raise SyntaxError(f"Esperado {tipo_esperado}, encontrado {tipo} ({valor})")

    def parse(self):
        comandos = self.cmd_list()
        return ProgramNode(comandos)

    def cmd_list(self):
        comandos = []
        while self.token_atual()[0] in ['KEYWORD', 'ID']:
            comandos.append(self.cmd())
        return comandos

    def cmd(self):
        tipo, val = self.token_atual()

        if tipo == 'KEYWORD' and val == 'int':
            # Verifica se é declaração de função no estilo C
            if self.tokens[self.pos + 1][0] == 'ID' and self.tokens[self.pos + 2][1] == '(':
                self.consumir('KEYWORD')  # consome 'int'
                nome = self.consumir('ID')
                self.consumir('SYMBOL')  # (
                params = self.param_list()
                self.consumir('SYMBOL')  # )
                body = self.bloco()
                return FuncDeclNode(nome, params, body)
            # Caso contrário, trata como declaração de variável
            self.consumir('KEYWORD')  # consome 'int'
            vars = []
            while True:
                nome = self.consumir('ID')
                valor = None
                if self.token_atual()[0] == 'OP' and self.token_atual()[1] == '=':
                    self.consumir('OP')  # consome '='
                    valor = self.exp()
                vars.append((nome, valor))
                if self.token_atual()[1] == ',':
                    self.consumir('SYMBOL')
                else:
                    break
            self.consumir('SYMBOL')  # consome ';'
            return DeclVarNode(vars)

        if val == 'return':
            self.consumir('KEYWORD')
            expr = self.exp()
            self.consumir('SYMBOL')  # ;
            return ReturnNode(expr)

        elif val == 'func':
            self.consumir('KEYWORD')
            nome = self.consumir('ID')
            self.consumir('SYMBOL')  # (
            params = self.param_list()
            self.consumir('SYMBOL')  # )
            body = self.bloco()
            return FuncDeclNode(nome, params, body)

        elif val == 'if':
            self.consumir('KEYWORD')
            self.consumir('SYMBOL')  # (
            cond = self.exp()
            self.consumir('SYMBOL')  # )
            then_body = self.bloco().comandos
            else_body = None
            if self.token_atual()[1] == 'else':
                self.consumir('KEYWORD')
                else_body = self.bloco().comandos
            return IfNode(cond, then_body, else_body)

        elif val == 'while':
            self.consumir('KEYWORD')
            self.consumir('SYMBOL')  # (
            cond = self.exp()
            self.consumir('SYMBOL')  # )
            body = self.bloco().comandos
            return WhileNode(cond, body)

        elif val == 'for':
            self.consumir('KEYWORD')
            self.consumir('SYMBOL')  # (
            init = self.atribuicao() if self.token_atual()[1] != ';' else None
            self.consumir('SYMBOL')  # ;
            cond = self.exp() if self.token_atual()[1] != ';' else None
            self.consumir('SYMBOL')  # ;
            inc = self.atribuicao() if self.token_atual()[1] != ')' else None
            self.consumir('SYMBOL')  # )
            body = self.bloco().comandos
            return ForNode(init, cond, inc, body)

        elif tipo == 'ID':
            lookahead = self.tokens[self.pos + 1][1] if self.pos + 1 < len(self.tokens) else ''
            if lookahead == '(':
                func_call = self.factor()
                self.consumir('SYMBOL')  # ;
                return func_call  # Chamadas são expressões e comandos aqui
            else:
                atrib = self.atribuicao()
                self.consumir('SYMBOL')  # ;
                return atrib

        else:
            raise SyntaxError(f"Comando inválido: {val}")

    def atribuicao(self):
        var = self.consumir('ID')
        op = self.consumir('OP')
        expr = self.exp()
        if op != '=':
            raise SyntaxError("Atribuição precisa usar '='")
        return AssignNode(var, expr)

    def exp(self):
        node = self.expr_or()
        return node

    def expr_or(self):
        node = self.expr_and()
        while self.token_atual()[0] == 'OP' and self.token_atual()[1] == '||':
            op = self.consumir('OP')
            right = self.expr_and()
            node = BinOpNode(op, node, right)
        return node

    def expr_and(self):
        node = self.expr_rel()
        while self.token_atual()[0] == 'OP' and self.token_atual()[1] == '&&':
            op = self.consumir('OP')
            right = self.expr_rel()
            node = BinOpNode(op, node, right)
        return node

    def expr_rel(self):
        node = self.expr_arit()
        while self.token_atual()[0] == 'OP' and self.token_atual()[1] in ('==', '!=', '<', '<=', '>', '>='):
            op = self.consumir('OP')
            right = self.expr_arit()
            node = BinOpNode(op, node, right)
        return node

    def expr_arit(self):
        node = self.term()
        while self.token_atual()[1] in ['+', '-']:
            op = self.consumir('OP')
            right = self.term()
            node = BinOpNode(op, node, right)
        return node

    def term(self):
        node = self.factor()
        while self.token_atual()[1] in ['*', '/']:
            op = self.consumir('OP')
            right = self.factor()
            node = BinOpNode(op, node, right)
        return node

    def factor(self):
        if self.token_atual()[0] == 'OP' and self.token_atual()[1] == '!':
            self.consumir('OP')
            node = self.factor()
            return UnaryOpNode('!', node)

        tipo, val = self.token_atual()
        if tipo == 'NUMBER':
            self.consumir('NUMBER')
            return NumberNode(int(val))
        elif tipo == 'ID':
            nome = self.consumir('ID')
            if self.token_atual()[1] == '(':
                self.consumir('SYMBOL')
                args = self.arg_list()
                self.consumir('SYMBOL')
                return FuncCallNode(nome, args)
            else:
                return VariableNode(nome)
        elif val == '(':
            self.consumir('SYMBOL')
            expr = self.exp()
            self.consumir('SYMBOL')
            return expr
        else:
            raise SyntaxError(f"Fator inválido: {val}")

    def bloco(self):
        self.consumir('SYMBOL')  # {
        comandos = self.cmd_list()
        self.consumir('SYMBOL')  # }
        return ProgramNode(comandos)

    def param_list(self):
        params = []
        while True:
            # Aceita e ignora o tipo 'int' antes do nome do parâmetro
            if self.token_atual()[0] == 'KEYWORD' and self.token_atual()[1] == 'int':
                self.consumir('KEYWORD')
            if self.token_atual()[0] == 'ID':
                params.append(self.consumir('ID'))
            else:
                break
            if self.token_atual()[1] == ',':
                self.consumir('SYMBOL')
            else:
                break
        return params

    def arg_list(self):
        args = []
        if self.token_atual()[0] != 'SYMBOL' or self.token_atual()[1] != ')':
            args.append(self.exp())
            while self.token_atual()[1] == ',':
                self.consumir('SYMBOL')
                args.append(self.exp())
        return args

class DeclVarNode(ASTNode):
    def __init__(self, vars):
        self.vars = vars  # lista de (nome, valor)

    def gerar_assembly(self, contexto):
        for nome, valor in self.vars:
            contexto.declarar_var(nome)
            if valor is not None:
                val_reg = valor.gerar_assembly(contexto)
                addr_reg = contexto.novo_reg()
                contexto.emit(f"la {addr_reg}, {nome}")
                contexto.emit(f"sw {val_reg}, 0({addr_reg})")

    def gerar_tac(self, contexto):
        for nome, valor in self.vars:
            if valor is not None:
                temp = valor.gerar_tac(contexto)
                contexto.emit(f"{nome} = {temp}")

    def verificar_semantica(self, contexto):
        for nome, valor in self.vars:
            if not contexto.foi_declarado(nome):
                contexto.declarar(nome, "variável")
            else:
                contexto.erros.append(f"Variável '{nome}' já declarada.")
            if valor is not None:
                valor.verificar_semantica(contexto)
