class ContextoSemantico:
    def __init__(self):
        self.escopos = [{}]
        self.erros = []
        self.funcoes = {}
        self.escopo_nomes = ["global"]  # Nome do escopo atual

    def entrar_escopo(self, nome):
        self.escopos.append({})
        self.escopo_nomes.append(nome)

    def sair_escopo(self):
        self.escopos.pop()
        self.escopo_nomes.pop()

    def declarar_funcao(self, nome, params):
        if nome in self.funcoes:
            self.erros.append(f"Função '{nome}' já declarada.")
        else:
            self.funcoes[nome] = len(params)

    def checar_funcao(self, nome, qtd_args):
        if nome not in self.funcoes:
            self.erros.append(f"Função '{nome}' não declarada.")
        elif self.funcoes[nome] != qtd_args:
            self.erros.append(f"Função '{nome}' chamada com {qtd_args} argumento(s), mas espera {self.funcoes[nome]}.")

    def foi_declarado(self, nome):
        # Procura do escopo mais interno para o mais externo
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return True
        return False

    def declarar(self, nome, tipo="variável"):
        escopo_atual = self.escopos[-1]
        escopo_nome = self.escopo_nomes[-1]
        if nome in escopo_atual:
            self.erros.append(f"{tipo.capitalize()} '{nome}' já declarada no escopo atual.")
        else:
            escopo_atual[nome] = {"tipo": tipo, "escopo": escopo_nome}

    def imprimir_erros(self):
        if not self.erros:
            print("Nenhum erro semântico encontrado.")
        else:
            print("Erros semânticos:")
            for erro in self.erros:
                print(erro)

    def imprimir_tabela(self):
        print("\nTabela de Símbolos:")
        print("Nome\tTipo\tEscopo")
        for i, escopo in enumerate(self.escopos):
            for nome, info in escopo.items():
                tipo = info["tipo"]
                escopo_nome = info["escopo"]
                print(f"{nome}\t{tipo}\t{escopo_nome}")
        if hasattr(self, "funcoes"):
            for nome, qtd in self.funcoes.items():
                print(f"{nome}\tfunção\tglobal")
