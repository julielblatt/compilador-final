class ContextoTAC:
    def __init__(self):
        self.temp_count = 0
        self.instrucoes = []

    def novo_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def emit(self, instrucao):
        self.instrucoes.append(instrucao)

    def imprimir(self):
        print("Código TAC gerado:")
        for instr in self.instrucoes:
            print(instr)
