VERMELHO = "V"
PRETO = "P"


class No:
    def __init__(self, chave, valor, cor):
        self.chave = chave
        self.valor = valor
        self.cor = cor
        self.esq = None
        self.dir = None
        self.pai = None


class ArvoreRubroNegra:
    def __init__(self):
        self.NIL = No(None, None, PRETO)
        self.raiz = self.NIL
        self.tamanho = 0
        self.rotacoes = 0

    def buscar(self, chave):
        no = self.raiz
        while no is not self.NIL and no.chave != chave:
            no = no.esq if chave < no.chave else no.dir
        return None if no is self.NIL else no

    def caminho(self, chave):
        visitados = []
        no = self.raiz
        while no is not self.NIL:
            visitados.append(no.chave)
            if chave == no.chave:
                break
            no = no.esq if chave < no.chave else no.dir
        return visitados

    def rotacao_esquerda(self, x):
        y = x.dir
        x.dir = y.esq
        if y.esq is not self.NIL:
            y.esq.pai = x
        self.trocar_filho(x, y)
        y.esq = x
        x.pai = y
        self.rotacoes += 1

    def rotacao_direita(self, x):
        y = x.esq
        x.esq = y.dir
        if y.dir is not self.NIL:
            y.dir.pai = x
        self.trocar_filho(x, y)
        y.dir = x
        x.pai = y
        self.rotacoes += 1

    def trocar_filho(self, antigo, novo):
        novo.pai = antigo.pai
        if antigo.pai is None:
            self.raiz = novo
        elif antigo is antigo.pai.esq:
            antigo.pai.esq = novo
        else:
            antigo.pai.dir = novo

    def inserir(self, chave, valor):
        novo = No(chave, valor, VERMELHO)
        novo.esq = self.NIL
        novo.dir = self.NIL

        pai = None
        no = self.raiz
        while no is not self.NIL:
            pai = no
            no = no.esq if chave < no.chave else no.dir
        novo.pai = pai
        if pai is None:
            self.raiz = novo
        elif chave < pai.chave:
            pai.esq = novo
        else:
            pai.dir = novo
        self.tamanho += 1

        self.consertar_insercao(novo)

    def consertar_insercao(self, z):
        while z.pai is not None and z.pai.cor == VERMELHO:
            avo = z.pai.pai
            pai_na_esquerda = z.pai is avo.esq
            tio = avo.dir if pai_na_esquerda else avo.esq

            if tio.cor == VERMELHO:
                z.pai.cor = PRETO
                tio.cor = PRETO
                avo.cor = VERMELHO
                z = avo
            else:
                if pai_na_esquerda:
                    if z is z.pai.dir:
                        z = z.pai
                        self.rotacao_esquerda(z)
                    z.pai.cor = PRETO
                    avo.cor = VERMELHO
                    self.rotacao_direita(avo)
                else:
                    if z is z.pai.esq:
                        z = z.pai
                        self.rotacao_direita(z)
                    z.pai.cor = PRETO
                    avo.cor = VERMELHO
                    self.rotacao_esquerda(avo)
        self.raiz.cor = PRETO

    def remover(self, chave):
        z = self.buscar(chave)
        if z is None:
            return False

        y = z
        cor_que_saiu = y.cor
        if z.esq is self.NIL:
            x = z.dir
            self.trocar_filho(z, z.dir)
        elif z.dir is self.NIL:
            x = z.esq
            self.trocar_filho(z, z.esq)
        else:
            y = z.dir
            while y.esq is not self.NIL:
                y = y.esq
            cor_que_saiu = y.cor
            x = y.dir
            if y.pai is z:
                x.pai = y
            else:
                self.trocar_filho(y, y.dir)
                y.dir = z.dir
                y.dir.pai = y
            self.trocar_filho(z, y)
            y.esq = z.esq
            y.esq.pai = y
            y.cor = z.cor
        self.tamanho -= 1

        if cor_que_saiu == PRETO:
            self.consertar_remocao(x)
        return True

    def consertar_remocao(self, x):
        while x is not self.raiz and x.cor == PRETO:
            na_esquerda = x is x.pai.esq
            irmao = x.pai.dir if na_esquerda else x.pai.esq

            if irmao.cor == VERMELHO:
                irmao.cor = PRETO
                x.pai.cor = VERMELHO
                self.girar(x.pai, na_esquerda)
                irmao = x.pai.dir if na_esquerda else x.pai.esq

            perto = irmao.esq if na_esquerda else irmao.dir
            longe = irmao.dir if na_esquerda else irmao.esq
            if perto.cor == PRETO and longe.cor == PRETO:
                irmao.cor = VERMELHO
                x = x.pai
            else:
                if longe.cor == PRETO:
                    perto.cor = PRETO
                    irmao.cor = VERMELHO
                    self.girar(irmao, not na_esquerda)
                    irmao = x.pai.dir if na_esquerda else x.pai.esq
                    longe = irmao.dir if na_esquerda else irmao.esq
                irmao.cor = x.pai.cor
                x.pai.cor = PRETO
                longe.cor = PRETO
                self.girar(x.pai, na_esquerda)
                x = self.raiz
        x.cor = PRETO

    def girar(self, no, para_esquerda):
        if para_esquerda:
            self.rotacao_esquerda(no)
        else:
            self.rotacao_direita(no)

    def em_ordem(self):
        resultado = []
        self.visitar(self.raiz, resultado)
        return resultado

    def visitar(self, no, resultado):
        if no is self.NIL:
            return
        self.visitar(no.esq, resultado)
        resultado.append(no.valor)
        self.visitar(no.dir, resultado)

    def altura(self, no=None):
        if no is None:
            no = self.raiz
        if no is self.NIL:
            return 0
        return 1 + max(self.altura(no.esq), self.altura(no.dir))

    def desenho(self):
        lista = []
        self.posicionar(self.raiz, 0, None, lista)
        for p in lista:
            for q in lista:
                if q.no is p.pai:
                    p.pai_coluna = q.coluna
                    p.pai_nivel = q.nivel
        return lista

    def posicionar(self, no, nivel, pai, lista):
        if no is self.NIL:
            return
        self.posicionar(no.esq, nivel + 1, no, lista)
        lista.append(Posicao(no, len(lista), nivel, pai))
        self.posicionar(no.dir, nivel + 1, no, lista)

    def valida(self):
        if self.raiz.cor != PRETO:
            return False
        return self.contar_pretos(self.raiz) != -1

    def contar_pretos(self, no):
        if no is self.NIL:
            return 1
        if no.cor == VERMELHO and (no.esq.cor == VERMELHO or no.dir.cor == VERMELHO):
            return -1
        esq = self.contar_pretos(no.esq)
        dir = self.contar_pretos(no.dir)
        if esq == -1 or esq != dir:
            return -1
        return esq + (1 if no.cor == PRETO else 0)

    def __len__(self):
        return self.tamanho


class Posicao:
    def __init__(self, no, coluna, nivel, pai):
        self.no = no
        self.coluna = coluna
        self.nivel = nivel
        self.pai = pai
        self.pai_coluna = None
        self.pai_nivel = None