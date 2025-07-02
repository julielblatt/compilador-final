from analisador_lexico import analisador_lexico
from my_parser import Parser
from contexto_tac import ContextoTAC
from contexto_assembly import ContextoAssembly
from contexto_semantico import ContextoSemantico
from imprimir_ast import print_ast
codigo ='''
int soma(int x, int y) {
    return x + y;
}
'''

tokens = analisador_lexico(codigo)
parser = Parser(tokens)
ast1 = parser.parse()
print("\nÁrvore Sintática (AST):")
print_ast(ast1)

# Semântica
ctx_sem = ContextoSemantico()
ast1.verificar_semantica(ctx_sem)
ctx_sem.imprimir_erros()
ctx_sem.imprimir_tabela()




# TAC
ctx_tac = ContextoTAC()
ast1.gerar_tac(ctx_tac)
ctx_tac.imprimir()

# Assembly
ctx_asm = ContextoAssembly()
ast1.gerar_assembly(ctx_asm)
ctx_asm.imprimir()

def gerar_assembly(self, contexto):
    val = self.value.gerar_assembly(contexto)
    contexto.emit(f"move $a0, {val}")
    contexto.emit("li $v0, 1")
    contexto.emit("syscall")
def imprimir(self):
    print("\n# Código Assembly gerado:")
    print(".data")
    for var in self.vars:
        print(f"{var}: .word 0")
    print(".text")
    print("main:")
    for linha in self.codigo:
        print(linha)
    print("li $v0, 10")
    print("syscall")



