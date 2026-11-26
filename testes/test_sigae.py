# Testes do SIGAE (cenários da seção 7 do enunciado)
# Rodar na pasta do projeto:   python -m unittest discover -s testes -v

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from estruturas import TabelaHash, MinHeap, ArvoreRubroNegra, funcao_hash
from sistema import Sistema, ErroSIGAE


def com_tres_medicos():
    s = Sistema()
    s.cadastrar_medico("A", "CRM-1")
    s.cadastrar_medico("B", "CRM-2")
    s.cadastrar_medico("C", "CRM-3")
    return s


class TestEstruturas(unittest.TestCase):

    def test_hash_colisao_igual_aula(self):
        # Theo (400) e Josi (405) caem na mesma posição numa tabela de 5
        self.assertEqual(funcao_hash("Theo", 5), funcao_hash("Josi", 5))
        t = TabelaHash(5)
        t.setar_item("Theo", "123")
        t.setar_item("Josi", "222")
        self.assertEqual(t.colisoes, 1)
        self.assertEqual(t.obter_item("Josi"), "222")

    def test_hash_redimensiona_e_remove(self):
        t = TabelaHash(5)
        for i in range(1, 21):
            t.setar_item(i, i * 10)
        self.assertGreater(t.redimensionamentos, 0)
        self.assertEqual(t.obter_item(15), 150)          # nada se perdeu
        self.assertTrue(t.remover_item(15))
        self.assertIsNone(t.obter_item(15))

    def test_heap_sai_em_ordem(self):
        class Item:
            def __init__(self, id):
                self.id = id
        h = MinHeap(lambda x: x.id)
        for v in [5, 3, 8, 1, 9, 2]:
            h.inserir(Item(v))
        h.remover(8)
        self.assertEqual([h.remover_topo().id for _ in range(5)], [1, 2, 3, 5, 9])

    def test_rubro_negra_insercao_em_ordem_fica_balanceada(self):
        a = ArvoreRubroNegra()
        for i in range(100):
            a.inserir(i, i)
            self.assertTrue(a.valida())
        self.assertGreater(a.rotacoes, 0)
        self.assertLessEqual(a.altura(), 14)             # árvore comum teria altura 100
        self.assertEqual(a.em_ordem(), list(range(100)))

    def test_rubro_negra_remocao(self):
        random.seed(1)
        a = ArvoreRubroNegra()
        chaves = random.sample(range(1000), 200)
        for c in chaves:
            a.inserir(c, c)
        for c in chaves[:150]:
            self.assertTrue(a.remover(c))
            self.assertTrue(a.valida())
        self.assertEqual(a.em_ordem(), sorted(chaves[150:]))


class TestCenarios(unittest.TestCase):

    def test_medicos_A_B_C_recebem_um_cada(self):
        s = com_tres_medicos()
        for i in range(3):
            s.cadastrar_paciente(f"P{i}", 3)
        nomes = [s.chamar_proximo().medico.nome for _ in range(3)]
        self.assertEqual(nomes, ["A", "B", "C"])

    def test_proximo_medico_tem_menos_concluidos(self):
        s = com_tres_medicos()
        for i in range(5):
            s.cadastrar_paciente(f"P{i}", 3)
        p1 = s.chamar_proximo()               # A
        p2 = s.chamar_proximo()               # B
        s.chamar_proximo()                    # C
        s.concluir(p1.id)                     # A = 1
        p4 = s.chamar_proximo()               # A de novo (único livre)
        s.concluir(p4.id)                     # A = 2
        s.concluir(p2.id)                     # B = 1
        # livres: A com 2 e B com 1 -> B
        self.assertEqual(s.chamar_proximo().medico.nome, "B")

    def test_empate_vai_para_quem_esta_ha_mais_tempo_sem_paciente(self):
        s = com_tres_medicos()
        for i in range(5):
            s.cadastrar_paciente(f"P{i}", 3)
        pa = s.chamar_proximo()               # A recebe (chamada 1)
        pb = s.chamar_proximo()               # B recebe (chamada 2)
        s.concluir(pb.id)                     # B = 1
        s.concluir(pa.id)                     # A = 1
        # A e B com 1; C com 0 -> C primeiro
        self.assertEqual(s.chamar_proximo().medico.nome, "C")
        # A e B empatados com 1: A recebeu paciente antes -> A
        self.assertEqual(s.chamar_proximo().medico.nome, "A")

    def test_sem_medico_livre_paciente_fica_na_fila(self):
        s = Sistema()
        s.cadastrar_medico("Único", "CRM-1")
        s.cadastrar_paciente("P1", 1)
        p2 = s.cadastrar_paciente("P2", 2)
        s.chamar_proximo()
        with self.assertRaises(ErroSIGAE):
            s.chamar_proximo()
        self.assertEqual(p2.situacao, "Aguardando")
        self.assertEqual(len(s.fila), 1)      # não sumiu nem duplicou
        self.assertEqual(len(s.arvore), 1)

    def test_ordem_respeita_risco_depois_chegada(self):
        s = Sistema()
        for i in range(5):
            s.cadastrar_medico(f"M{i}", f"CRM-{i}")
        s.cadastrar_paciente("Nao urgente", 5, "07:00:00")
        s.cadastrar_paciente("Urgente cedo", 3, "07:10:00")
        s.cadastrar_paciente("Emergencia", 1, "07:30:00")
        s.cadastrar_paciente("Urgente tarde", 3, "07:20:00")
        ordem = [s.chamar_proximo().nome for _ in range(4)]
        self.assertEqual(ordem, ["Emergencia", "Urgente cedo", "Urgente tarde", "Nao urgente"])

    def test_reclassificar_nao_duplica(self):
        s = com_tres_medicos()
        s.cadastrar_paciente("P1", 3)
        p2 = s.cadastrar_paciente("P2", 5)
        s.reclassificar(p2.id, 1)
        self.assertEqual(len(s.fila), 2)
        self.assertEqual(s.chamar_proximo().id, p2.id)

    def test_cancelar_nao_conta_atendimento(self):
        s = com_tres_medicos()
        p = s.cadastrar_paciente("P1", 3)
        s.chamar_proximo()
        s.cancelar(p.id)
        a = s.medicos.obter_item(1)
        self.assertEqual(a.concluidos, 0)
        self.assertEqual(a.situacao, "Disponível")
        self.assertEqual(len(s.livres), 3)    # médico voltou para o heap

    def test_excluir_tira_de_todas_as_estruturas(self):
        s = Sistema()
        p = s.cadastrar_paciente("Cadastro errado", 3)
        s.excluir(p.id)
        self.assertIsNone(s.pacientes.obter_item(p.id))   # saiu da Hash
        self.assertEqual(len(s.fila), 0)                  # saiu do Heap
        self.assertEqual(len(s.arvore), 0)                # saiu da Árvore

    def test_hash_e_arvore_dentro_do_sistema(self):
        s = Sistema()
        for i in range(30):
            s.cadastrar_paciente(f"P{i}", 3)
        self.assertGreater(s.pacientes.colisoes, 0)
        self.assertGreater(s.pacientes.redimensionamentos, 0)
        self.assertEqual(s.buscar_paciente(12).nome, "P11")
        self.assertTrue(s.arvore.valida())

    def test_muitas_operacoes_sem_orfaos(self):
        random.seed(7)
        s = Sistema()
        for i in range(3):
            s.cadastrar_medico(f"M{i}", f"CRM{i}")
        for _ in range(400):
            acao = random.random()
            alvo = random.randint(1, s.proximo_paciente)
            try:
                if acao < 0.35:
                    s.cadastrar_paciente("X", random.randint(1, 5))
                elif acao < 0.6:
                    s.chamar_proximo()
                elif acao < 0.8:
                    s.concluir(alvo)
                elif acao < 0.9:
                    s.reclassificar(alvo, random.randint(1, 5))
                else:
                    s.cancelar(alvo)
            except ErroSIGAE:
                pass
            aguardando = [p for p in s.chegadas if p.situacao == "Aguardando"]
            self.assertEqual(len(aguardando), len(s.fila))     # heap bate com a situação
            self.assertEqual(len(aguardando), len(s.arvore))   # árvore bate com a situação
            self.assertTrue(s.arvore.valida())
        total = sum(m.concluidos for m in s.medicos.valores())
        self.assertEqual(total, sum(1 for p in s.chegadas if p.situacao == "Concluído"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
