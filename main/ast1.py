class ASTNode:
    def gerar_tac(self, contexto):
        raise NotImplementedError()

    def verificar_semantica(self, contexto):
        raise NotImplementedError()


class ProgramNode(ASTNode):
    def __init__(self, comandos):
        self.comandos = comandos


    def gerar_tac(self, contexto):
        for cmd in self.comandos:
            cmd.gerar_tac(contexto)

    def gerar_assembly(self, contexto):
        for cmd in self.comandos:
            cmd.gerar_assembly(contexto)

    def verificar_semantica(self, contexto):
        for cmd in self.comandos:
            cmd.verificar_semantica(contexto)


class AssignNode(ASTNode):
    def __init__(self, var, value):
        self.var = var
        self.value = value


    def gerar_tac(self, contexto):
        temp = self.value.gerar_tac(contexto)
        contexto.emit(f"{self.var} = {temp}")

    def gerar_assembly(self, contexto):
        contexto.declarar_var(self.var)
        val = self.value.gerar_assembly(contexto)
        addr_reg = contexto.novo_reg()
        contexto.emit(f"la {addr_reg}, {self.var}")
        contexto.emit(f"sw {val}, 0({addr_reg})")

    def verificar_semantica(self, contexto):
        if not contexto.foi_declarado(self.var):
            contexto.declarar(self.var, "variável")
        self.value.verificar_semantica(contexto)


class ReturnNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def gerar_tac(self, contexto):
        temp = self.value.gerar_tac(contexto)
        contexto.emit(f"return {temp}")

    def gerar_assembly(self, contexto):
        val = self.value.gerar_assembly(contexto)
        contexto.emit(f"mv a0, {val}")
        

    def verificar_semantica(self, contexto):
        self.value.verificar_semantica(contexto)


class BinOpNode(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


    def gerar_tac(self, contexto):
        t1 = self.left.gerar_tac(contexto)
        t2 = self.right.gerar_tac(contexto)
        temp = contexto.novo_temp()
        contexto.emit(f"{temp} = {t1} {self.op} {t2}")
        return temp

    def gerar_assembly(self, contexto):
        l = self.left.gerar_assembly(contexto)
        r = self.right.gerar_assembly(contexto)
        dest = contexto.novo_reg()
        if self.op == '+':
            contexto.emit(f"add {dest}, {l}, {r}")
        elif self.op == '-':
            contexto.emit(f"sub {dest}, {l}, {r}")
        elif self.op == '*':
            contexto.emit(f"mul {dest}, {l}, {r}")
        elif self.op == '/':
            contexto.emit(f"div {dest}, {l}, {r}")
        elif self.op == '==':
            contexto.emit(f"sub {dest}, {l}, {r}")
            contexto.emit(f"seqz {dest}, {dest}")
        elif self.op == '!=':
            contexto.emit(f"sub {dest}, {l}, {r}")
            contexto.emit(f"snez {dest}, {dest}")
        elif self.op == '<':
            contexto.emit(f"slt {dest}, {l}, {r}")
        elif self.op == '<=':
            contexto.emit(f"slt {dest}, {r}, {l}")
            contexto.emit(f"xori {dest}, {dest}, 1")
        elif self.op == '>':
            contexto.emit(f"slt {dest}, {r}, {l}")
        elif self.op == '>=':
            contexto.emit(f"slt {dest}, {l}, {r}")
            contexto.emit(f"xori {dest}, {dest}, 1")
        elif self.op == '&&':
            contexto.emit(f"snez {l}, {l}")
            contexto.emit(f"snez {r}, {r}")
            contexto.emit(f"and {dest}, {l}, {r}")
        elif self.op == '||':
            contexto.emit(f"snez {l}, {l}")
            contexto.emit(f"snez {r}, {r}")
            contexto.emit(f"or {dest}, {l}, {r}")
        else:
            contexto.emit(f"# Operador não suportado: {self.op}")
        return dest  

    def verificar_semantica(self, contexto):
        self.left.verificar_semantica(contexto)
        self.right.verificar_semantica(contexto)


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value


    def gerar_tac(self, contexto):
        return str(self.value)

    def gerar_assembly(self, contexto):
        reg = contexto.novo_reg()
        contexto.emit(f"li {reg}, {self.value}")
        return reg

    def verificar_semantica(self, contexto):
        pass  


class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name


    def gerar_tac(self, contexto):
        return self.name

    def gerar_assembly(self, contexto):
        contexto.declarar_var(self.name)
        addr_reg = contexto.novo_reg()
        val_reg = contexto.novo_reg()
        contexto.emit(f"la {addr_reg}, {self.name}")
        contexto.emit(f"lw {val_reg}, 0({addr_reg})")
        return val_reg

    def verificar_semantica(self, contexto):
        if not contexto.foi_declarado(self.name):
            contexto.erros.append(f"Erro: variável '{self.name}' usada mas não declarada")


class FuncDeclNode(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def gerar_tac(self, contexto):
        contexto.emit(f"func {self.name}({', '.join(self.params)})")
        self.body.gerar_tac(contexto)
        contexto.emit("endfunc")

    def gerar_assembly(self, contexto):
        contexto.emit(f"{self.name}:")
       
        for i, param in enumerate(self.params):
            contexto.declarar_var(param)
            addr_reg = contexto.novo_reg()
            contexto.emit(f"la {addr_reg}, {param}")
            contexto.emit(f"sw a{i}, 0({addr_reg})")
        for cmd in self.body.comandos:
            cmd.gerar_assembly(contexto)
        contexto.emit("ret")

    def verificar_semantica(self, contexto):
        contexto.declarar_funcao(self.name, self.params)
        contexto.entrar_escopo(self.name)
        for param in self.params:
            contexto.declarar(param)
        for cmd in self.body.comandos:  
            cmd.verificar_semantica(contexto)
        contexto.sair_escopo()


class FuncCallNode(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def gerar_tac(self, contexto):
        temps = [arg.gerar_tac(contexto) for arg in self.args]
        temp = contexto.novo_temp()
        contexto.emit(f"{temp} = call {self.name}({', '.join(temps)})")
        return temp

    def gerar_assembly(self, contexto):
        
        arg_regs = ['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7']
        for i, arg in enumerate(self.args):
            val = arg.gerar_assembly(contexto)
            contexto.emit(f"mv {arg_regs[i]}, {val}")
        contexto.emit(f"call {self.name}")  
       
        dest = contexto.novo_reg()
        contexto.emit(f"mv {dest}, a0")
        return dest

    def verificar_semantica(self, contexto):
        contexto.checar_funcao(self.name, len(self.args))
        for arg in self.args:
            arg.verificar_semantica(contexto)


class IfNode(ASTNode):
    def __init__(self, cond, then_body, else_body=None):
        self.cond = cond
        self.then_body = then_body
        self.else_body = else_body

    def gerar_assembly(self, contexto):
        cond_reg = self.cond.gerar_assembly(contexto)
        label_else = contexto.nova_label("ELSE")
        label_end = contexto.nova_label("ENDIF")
        contexto.emit(f"beq {cond_reg}, zero, {label_else}")
        for cmd in self.then_body:
            cmd.gerar_assembly(contexto)
        contexto.emit(f"j {label_end}")
        contexto.emit(f"{label_else}:")
        if self.else_body:
            for cmd in self.else_body:
                cmd.gerar_assembly(contexto)
        contexto.emit(f"{label_end}:")

    def gerar_tac(self, contexto):
        cond = self.cond.gerar_tac(contexto)
        label_else = f"else_{id(self)}"
        label_end = f"endif_{id(self)}"
        contexto.emit(f"ifnot {cond} goto {label_else}")
        for cmd in self.then_body:
            cmd.gerar_tac(contexto)
        contexto.emit(f"goto {label_end}")
        contexto.emit(f"{label_else}:")
        if self.else_body:
            for cmd in self.else_body:
                cmd.gerar_tac(contexto)
        contexto.emit(f"{label_end}:")

    def verificar_semantica(self, contexto):
        self.cond.verificar_semantica(contexto)
        for cmd in self.then_body:
            cmd.verificar_semantica(contexto)
        if self.else_body:
            for cmd in self.else_body:
                cmd.verificar_semantica(contexto)

class WhileNode(ASTNode):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def gerar_assembly(self, contexto):
        label_start = contexto.nova_label("WHILE")
        label_end = contexto.nova_label("ENDWHILE")
        contexto.emit(f"{label_start}:")
        cond_reg = self.cond.gerar_assembly(contexto)
        contexto.emit(f"beq {cond_reg}, zero, {label_end}")
        for cmd in self.body:
            cmd.gerar_assembly(contexto)
        contexto.emit(f"j {label_start}")
        contexto.emit(f"{label_end}:")

    def gerar_tac(self, contexto):
        label_start = f"while_{id(self)}"
        label_end = f"endwhile_{id(self)}"
        contexto.emit(f"{label_start}:")
        cond = self.cond.gerar_tac(contexto)
        contexto.emit(f"ifnot {cond} goto {label_end}")
        for cmd in self.body:
            cmd.gerar_tac(contexto)
        contexto.emit(f"goto {label_start}")
        contexto.emit(f"{label_end}:")

    def verificar_semantica(self, contexto):
        self.cond.verificar_semantica(contexto)
        for cmd in self.body:
            cmd.verificar_semantica(contexto)

class ForNode(ASTNode):
    def __init__(self, init, cond, inc, body):
        self.init = init      
        self.cond = cond      
        self.inc = inc        
        self.body = body      

    def gerar_assembly(self, contexto):
        if self.init:
            self.init.gerar_assembly(contexto)
        label_start = contexto.nova_label("FOR")
        label_end = contexto.nova_label("ENDFOR")
        contexto.emit(f"{label_start}:")
        cond_reg = self.cond.gerar_assembly(contexto)
        contexto.emit(f"beq {cond_reg}, zero, {label_end}")
        for cmd in self.body:
            cmd.gerar_assembly(contexto)
        if self.inc:
            self.inc.gerar_assembly(contexto)
        contexto.emit(f"j {label_start}")
        contexto.emit(f"{label_end}:")

    def gerar_tac(self, contexto):
        if self.init:
            self.init.gerar_tac(contexto)
        label_start = f"for_{id(self)}"
        label_end = f"endfor_{id(self)}"
        contexto.emit(f"{label_start}:")
        cond = self.cond.gerar_tac(contexto)
        contexto.emit(f"ifnot {cond} goto {label_end}")
        for cmd in self.body:
            cmd.gerar_tac(contexto)
        if self.inc:
            self.inc.gerar_tac(contexto)
        contexto.emit(f"goto {label_start}")
        contexto.emit(f"{label_end}:")

    def verificar_semantica(self, contexto):
        if self.init:
            self.init.verificar_semantica(contexto)
        if self.cond:
            self.cond.verificar_semantica(contexto)
        if self.inc:
            self.inc.verificar_semantica(contexto)
        for cmd in self.body:
            cmd.verificar_semantica(contexto)

class UnaryOpNode(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def gerar_assembly(self, contexto):
        val = self.expr.gerar_assembly(contexto)
        dest = contexto.novo_reg()
        if self.op == '!':
            contexto.emit(f"seqz {dest}, {val}")  
        else:
            contexto.emit(f"# Operador unário não suportado: {self.op}")
        return dest

    def verificar_semantica(self, contexto):
        self.expr.verificar_semantica(contexto)

class ContextoAssembly:
    def __init__(self):
        self.codigo = []
        self.labels = 0
        self.vars = set()
        self.reg_count = 0

    def emit(self, linha):
        self.codigo.append(linha)

    def nova_label(self, prefixo="L"):
        label = f"{prefixo}{self.labels}"
        self.labels += 1
        return label

    def declarar_var(self, nome):
        self.vars.add(nome)

    def novo_reg(self):
        reg = f"t{self.reg_count % 7}"  
        self.reg_count += 1
        return reg

    def imprimir(self):
        print("\n# Código Assembly RISC-V gerado:")
        print(".data")
        for var in self.vars:
            print(f"{var}: .word 0")
        print(".text")
        print(".globl main")
        print("main:")
        for linha in self.codigo:
            print(linha)
        print("li a7, 93")
        print("ecall")
