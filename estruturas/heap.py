# HEAP BINÁRIO MÍNIMO (Min-Heap)
# Uma árvore guardada dentro de uma lista. O menor fica sempre na posição 0.
#   pai de i = (i - 1) // 2      filhos de i = 2*i + 1  e  2*i + 2
# "prioridade" é uma função que devolve a tupla usada para comparar.
#   Pacientes: (risco, chegada, ID)      Médicos: (concluídos, última chamada, ID)


class MinHeap:
    def __init__(self, prioridade):
        self.itens = []
        self.prioridade = prioridade

    def inserir(self, item):
        self.itens.append(item)               # entra no final...
        self.subir(len(self.itens) - 1)       # ...e sobe até o lugar certo

    def topo(self):
        if len(self.itens) == 0:
            return None
        return self.itens[0]

    def remover_topo(self):
        if len(self.itens) == 0:
            return None
        primeiro = self.itens[0]
        ultimo = self.itens.pop()
        if len(self.itens) > 0:
            self.itens[0] = ultimo            # o último vai para o topo...
            self.descer(0)                    # ...e desce até o lugar certo
        return primeiro

    def remover(self, id_item):
        # usado para reclassificar e cancelar (remove sem deixar duplicado)
        for i in range(len(self.itens)):
            if self.itens[i].id == id_item:
                ultimo = self.itens.pop()
                if i < len(self.itens):
                    self.itens[i] = ultimo
                    self.subir(i)
                    self.descer(i)
                return True
        return False

    def subir(self, i):
        while i > 0:
            pai = (i - 1) // 2
            if self.menor(i, pai):
                self.itens[i], self.itens[pai] = self.itens[pai], self.itens[i]
                i = pai
            else:
                break

    def descer(self, i):
        while True:
            esq = 2 * i + 1
            dir = 2 * i + 2
            menor = i
            if esq < len(self.itens) and self.menor(esq, menor):
                menor = esq
            if dir < len(self.itens) and self.menor(dir, menor):
                menor = dir
            if menor == i:
                break
            self.itens[i], self.itens[menor] = self.itens[menor], self.itens[i]
            i = menor

    def menor(self, a, b):
        return self.prioridade(self.itens[a]) < self.prioridade(self.itens[b])

    def em_ordem(self):
        # cópia tirada em ordem, só para mostrar a fila na tela
        copia = MinHeap(self.prioridade)
        copia.itens = list(self.itens)
        resultado = []
        while len(copia.itens) > 0:
            resultado.append(copia.remover_topo())
        return resultado

    def __len__(self):
        return len(self.itens)
