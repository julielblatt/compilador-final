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
