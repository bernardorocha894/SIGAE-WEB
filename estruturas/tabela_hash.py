# TABELA HASH
# A chave (ID) calcula a posição onde o dado fica, sem precisar procurar um por um.
# Colisão: tratada por encadeamento (cada posição é uma lista).
# Quando enche (mais de 75%), a tabela dobra de tamanho.


def funcao_hash(chave, tamanho):
    soma = 0
    for c in str(chave):
        soma = soma + ord(c)          # soma o código de cada caractere
    return soma % tamanho             # resto da divisão = posição


class TabelaHash:
    def __init__(self, tamanho=5):
        self.tamanho = tamanho
        self.tabela = [[] for _ in range(tamanho)]
        self.quantidade = 0
        self.colisoes = 0
        self.redimensionamentos = 0

    def setar_item(self, chave, valor):
        posicao = funcao_hash(chave, self.tamanho)
        lista = self.tabela[posicao]
        for par in lista:
            if par[0] == chave:       # chave já existe: só atualiza
                par[1] = valor
                return
        if len(lista) > 0:            # já tinha alguém aqui: colisão
            self.colisoes += 1
        lista.append([chave, valor])
        self.quantidade += 1
        if self.quantidade / self.tamanho > 0.75:
            self.redimensionar()

    def obter_item(self, chave):
        posicao = funcao_hash(chave, self.tamanho)
        for par in self.tabela[posicao]:
            if par[0] == chave:
                return par[1]
        return None

    def remover_item(self, chave):
        posicao = funcao_hash(chave, self.tamanho)
        lista = self.tabela[posicao]
        for i in range(len(lista)):
            if lista[i][0] == chave:
                lista.pop(i)
                self.quantidade -= 1
                return True
        return False

    def redimensionar(self):
        antiga = self.tabela
        self.tamanho = self.tamanho * 2
        self.tabela = [[] for _ in range(self.tamanho)]
        self.redimensionamentos += 1
        for lista in antiga:                  # recoloca todo mundo na tabela nova
            for chave, valor in lista:
                self.tabela[funcao_hash(chave, self.tamanho)].append([chave, valor])

    def valores(self):
        resultado = []
        for lista in self.tabela:
            for par in lista:
                resultado.append(par[1])
        return resultado
