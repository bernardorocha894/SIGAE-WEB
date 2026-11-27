# REGRAS DO SIGAE
# Aqui as estruturas trabalham juntas:
#   pacientes  (Tabela Hash)   ID -> paciente            achar pelo ID
#   medicos    (Tabela Hash)   ID -> médico              achar pelo ID
#   fila       (Min-Heap)      (risco, chegada, ID)      paciente mais urgente
#   livres     (Min-Heap)      (concluídos, última chamada, ID)  médico com menos atendimentos
#   arvore     (Rubro-Negra)   (chegada, ID)             quem está esperando, em ordem de chegada

from datetime import datetime

from estruturas import TabelaHash, MinHeap, ArvoreRubroNegra

RISCOS = ["", "Emergência", "Muito urgente", "Urgente", "Pouco urgente", "Não urgente"]


class ErroSIGAE(Exception):
    pass


def agora():
    return datetime.now().strftime("%H:%M:%S")


class Paciente:
    def __init__(self, id, nome, risco, chegada):
        self.id = id
        self.nome = nome
        self.risco = risco              # 1 = Emergência ... 5 = Não urgente
        self.chegada = chegada          # "HH:MM:SS"
        self.situacao = "Aguardando"
        self.medico = None
        self.inicio = None
        self.fim = None

    def nome_risco(self):
        return RISCOS[self.risco]

    def chave(self):
        return (self.chegada, self.id)


class Medico:
    def __init__(self, id, nome, crm):
        self.id = id
        self.nome = nome
        self.crm = crm
        self.situacao = "Disponível"
        self.concluidos = 0
        self.ultima_chamada = 0         # 0 = nunca recebeu paciente
        self.paciente = None


class Sistema:
    def __init__(self):
        self.pacientes = TabelaHash()
        self.medicos = TabelaHash()
        self.fila = MinHeap(lambda p: (p.risco, p.chegada, p.id))
        self.livres = MinHeap(lambda m: (m.concluidos, m.ultima_chamada, m.id))
        self.arvore = ArvoreRubroNegra()
        self.chegadas = []              # todos os pacientes, na ordem em que chegaram
        self.eventos = []
        self.proximo_paciente = 1
        self.proximo_medico = 1
        self.chamadas = 0

    def registrar(self, texto):
        self.eventos.append((agora(), texto))

    # ---------------- cadastros ----------------

    def cadastrar_paciente(self, nome, risco, chegada=None):
        if not nome or not nome.strip():
            raise ErroSIGAE("Informe o nome do paciente.")
        risco = int(risco)
        if risco < 1 or risco > 5:
            raise ErroSIGAE("O risco vai de 1 a 5.")
        p = Paciente(self.proximo_paciente, nome.strip(), risco, chegada or agora())
        self.proximo_paciente += 1

        self.pacientes.setar_item(p.id, p)   # Hash
        self.fila.inserir(p)                 # Heap
        self.arvore.inserir(p.chave(), p)    # Rubro-Negra
        self.chegadas.append(p)
        self.registrar(f"Paciente #{p.id} {p.nome} chegou ({p.nome_risco()}).")
        return p

    def cadastrar_medico(self, nome, crm):
        if not nome or not nome.strip() or not crm or not crm.strip():
            raise ErroSIGAE("Informe nome e registro do médico.")
        m = Medico(self.proximo_medico, nome.strip(), crm.strip())
        self.proximo_medico += 1
        self.medicos.setar_item(m.id, m)     # Hash
        self.livres.inserir(m)               # Heap de médicos livres
        self.registrar(f"Médico #{m.id} {m.nome} cadastrado.")
        return m

    def buscar_paciente(self, id):
        p = self.pacientes.obter_item(int(id))
        if p is None:
            raise ErroSIGAE(f"Paciente #{id} não encontrado.")
        return p

    # ---------------- triagem ----------------

    def reclassificar(self, id, novo_risco):
        p = self.buscar_paciente(id)
        if p.situacao != "Aguardando":
            raise ErroSIGAE("Só dá para reclassificar quem está aguardando.")
        self.fila.remover(p.id)              # tira do heap...
        p.risco = int(novo_risco)
        self.fila.inserir(p)                 # ...e coloca de novo: sem duplicar
        self.registrar(f"Paciente #{p.id} reclassificado para {p.nome_risco()}.")

    # ---------------- atendimento ----------------

    def chamar_proximo(self):
        paciente = self.fila.topo()          # primeiro só OLHA
        if paciente is None:
            raise ErroSIGAE("Não há pacientes na fila.")
        medico = self.livres.topo()
        if medico is None:
            raise ErroSIGAE(f"Nenhum médico livre. {paciente.nome} continua na fila.")

        self.fila.remover_topo()             # agora sim TIRA
        self.arvore.remover(paciente.chave())
        self.livres.remover_topo()

        self.chamadas += 1
        medico.ultima_chamada = self.chamadas
        medico.situacao = "Em atendimento"
        medico.paciente = paciente
        paciente.situacao = "Em atendimento"
        paciente.medico = medico
        paciente.inicio = agora()
        self.registrar(f"#{paciente.id} {paciente.nome} chamado por {medico.nome}.")
        return paciente

    def concluir(self, id):
        p = self.buscar_paciente(id)
        if p.situacao != "Em atendimento":
            raise ErroSIGAE("Esse paciente não está em atendimento.")
        p.situacao = "Concluído"
        p.fim = agora()
        p.medico.concluidos += 1             # só conta quando conclui
        self.liberar(p.medico)
        self.registrar(f"#{p.id} {p.nome} concluído por {p.medico.nome}.")

    def cancelar(self, id):
        p = self.buscar_paciente(id)
        if p.situacao == "Aguardando":       # estava na fila
            self.fila.remover(p.id)
            self.arvore.remover(p.chave())
        elif p.situacao == "Em atendimento":  # estava com médico: libera sem contar
            p.fim = agora()
            self.liberar(p.medico)
        else:
            raise ErroSIGAE(f"Esse paciente já está {p.situacao.lower()}.")
        p.situacao = "Cancelado"
        self.registrar(f"#{p.id} {p.nome} cancelado.")

    def excluir(self, id):
        # apaga um cadastro feito por engano (só de quem ainda está aguardando)
        p = self.buscar_paciente(id)
        if p.situacao != "Aguardando":
            raise ErroSIGAE("Só dá para excluir quem ainda está aguardando.")
        self.fila.remover(p.id)              # sai do Heap
        self.arvore.remover(p.chave())       # sai da Rubro-Negra
        self.pacientes.remover_item(p.id)    # sai da Tabela Hash
        self.chegadas.remove(p)
        self.registrar(f"Cadastro de #{p.id} {p.nome} excluído.")

    def liberar(self, medico):
        medico.situacao = "Disponível"
        medico.paciente = None
        self.livres.inserir(medico)          # volta ao heap com o contador novo

    # ---------------- consultas para as telas ----------------

    def buscar_pacientes(self, texto):
        # número: busca direto na Tabela Hash; nome: procura quem tem esse trecho no nome
        texto = (texto or "").strip()
        if texto.isdigit():
            p = self.pacientes.obter_item(int(texto))
            return [p] if p else []
        texto = texto.lower()
        return [p for p in self.chegadas if texto in p.nome.lower()]

    def buscar_medicos(self, texto="", situacao=""):
        # filtra por ID (Tabela Hash de médicos) ou nome, e pela situação
        texto = (texto or "").strip()
        if texto.isdigit():
            m = self.medicos.obter_item(int(texto))
            medicos = [m] if m else []
        else:
            medicos = [m for m in self.lista_medicos() if texto.lower() in m.nome.lower()]
        if situacao:
            medicos = [m for m in medicos if m.situacao == situacao]
        return medicos

    def lista_medicos(self):
        medicos = self.medicos.valores()
        medicos.sort(key=lambda m: m.id)
        return medicos

    def em_atendimento(self):
        return [p for p in self.chegadas if p.situacao == "Em atendimento"]

    def contagem(self):
        estados = ["Aguardando", "Em atendimento", "Concluído", "Cancelado"]
        return [(e, sum(1 for p in self.chegadas if p.situacao == e)) for e in estados]
