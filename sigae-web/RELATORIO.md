# Relatório técnico — SIGAE WEB

## Estruturas

**Tabela Hash** (`estruturas/tabela_hash.py`)
- Função: soma dos códigos dos caracteres do ID, resto da divisão pelo tamanho.
- Colisão: encadeamento (cada posição é uma lista).
- Redimensionamento: quando passa de 75% cheia, dobra de tamanho e recoloca todos.
- Uso: achar paciente e médico pelo ID. Custo médio O(1).

**Heap Binário** (`estruturas/heap.py`)
- Min-Heap guardado em lista: pai de i = (i-1)//2, filhos 2i+1 e 2i+2.
- Pacientes: chave (risco, chegada, ID). Médicos livres: (concluídos, última chamada, ID).
- Reclassificar = remover e inserir de novo (não duplica). Inserir e tirar o topo: O(log n).

**Árvore Rubro-Negra** (`estruturas/arvore_rubro_negra.py`)
- Chave (horário de chegada, ID). Guarda os pacientes que estão aguardando.
- Inserção com os casos 1 (recolorir), 2 e 3 (rotações); remoção com os 4 casos.
- Busca, inserção e remoção: O(log n). Percurso em ordem = ordem de chegada.

## Fluxo de chamada

1. Olha o topo do heap de pacientes e o topo do heap de médicos.
2. Se faltar algum, avisa e não remove nada (o paciente continua na fila).
3. Se tiver os dois, tira o paciente do heap e da árvore, e o médico do heap de livres.
4. Concluir soma 1 no médico e devolve ele ao heap. Cancelar devolve sem somar.

## Restrições

Não foram usados `dict`, `heapq` nem bibliotecas de árvore. Listas do Python são usadas como vetor.
O Flask usa dicionários internamente, mas isso faz parte do servidor web, não das estruturas.

## Testes

`testes/test_sigae.py`: 14 testes cobrindo Hash (colisão, redimensionamento, remoção), Heap,
Rubro-Negra (100 inserções em ordem, 150 remoções) e todos os cenários da seção 7.
