# SIGAE WEB

Simulador de pronto atendimento (trabalho de Estrutura de Dados Avançados). Todos os dados são fictícios.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

Abra **http://127.0.0.1:5000** no navegador.

## Como rodar os testes

```bash
python -m unittest discover -s testes -v
```

## Arquivos

```
app.py                          telas e botões (Flask)
sistema.py                      regras: cadastrar, chamar, concluir, cancelar
estruturas/tabela_hash.py       Tabela Hash (achar pelo ID)
estruturas/heap.py              Min-Heap (paciente mais urgente e médico com menos atendimentos)
estruturas/arvore_rubro_negra.py  Árvore Rubro-Negra (pacientes aguardando, em ordem de chegada)
templates/                      telas HTML
testes/test_sigae.py            testes
```

## Telas

Painel geral, Pacientes, Triagem e fila, Médicos, Atendimentos, Histórico e Árvore Rubro-Negra
(desenho da árvore; clicando em um paciente aparece o caminho da busca).

## Roteiro para demonstrar

1. Cadastre 3 médicos e 3 pacientes. Chame 3 vezes: vai um paciente para cada médico.
2. Cadastre pacientes com riscos diferentes: a Triagem mostra o mais urgente primeiro.
3. Com todos os médicos ocupados, "Chamar próximo" avisa e o paciente continua na fila.
4. Conclua e cancele atendimentos: só o concluído conta para o médico.
5. Cadastre vários pacientes e abra a tela Árvore Rubro-Negra.
