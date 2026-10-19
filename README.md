# AEDII — Aula 9: Saindo do Labirinto

Atividade da disciplina **Algoritmos e Estrutura de Dados II (AEDII)**, prof. Pablo De Chiaro — implementação de **DFS**, **BFS** e **Busca Gulosa (greedy best-first)** para encontrar a saída de um labirinto, representando cada casa livre como vértice de um grafo.

## O labirinto desenvolvido

Labirinto próprio de **12 × 12** (maior que o mínimo de 10 × 10 pedido), usando a mesma notação do material do professor:

- `I` → início
- `F` → fim (saída)
- `#` → parede
- `.` → casa livre

```
I...#.......
.##.#.#####.
.#..#.#...#.
.#.##.#.#.#.
.#....#.#...
.######.####
.#......#...
.#.####.#.#.
...#....#.#.
.###.####.#.
.#...#....#.
...#...##..F
```

O labirinto foi desenhado com três características de propósito, para deixar as diferenças entre os algoritmos bem visíveis:

- **Duas rotas até a saída, de tamanhos bem diferentes**: uma curta, descendo direto pela coluna 0 (26 passos), e outra longa, passando por cima e pela direita (60 passos).
- **A rota longa fica do lado que a DFS testa primeiro** (a ordem de vizinhos é ↑ → ↓ ←, ou seja, ela tenta ir para a direita antes de descer), então a DFS "cai" na rota longa e não troca por uma melhor.
- **Vários becos sem saída** espalhados pelo labirinto, para forçar as buscas a voltar (backtracking) e para que a quantidade de casas visitadas por cada algoritmo seja bem diferente.

## O que foi implementado

Todo o código está em [`labirinto.py`](./labirinto.py), comentado linha a linha.

- `achar`, `livre`, `montar_grafo`, `desenhar` — funções-base do material do professor, reaproveitadas sem alteração. `montar_grafo` transforma o labirinto num grafo (dicionário de lista de adjacência); `desenhar` imprime o labirinto marcando o caminho encontrado com `*`.
- `reconstruir(pai, saida)` — a partir do dicionário `pai` (quem descobriu cada casa), reconstrói o caminho do início até a saída, de trás para frente.
- `dfs(grafo, inicio, saida)` — busca em profundidade, usando a própria recursão como pilha. Mergulha no primeiro vizinho não visitado, na ordem ↑ → ↓ ←, e só volta quando bate num beco.
- `bfs(grafo, inicio, saida)` — busca em largura, usando uma fila (`deque`). Explora o labirinto em camadas de distância a partir do início.
- `gulosa(grafo, inicio, saida)` — busca gulosa (greedy best-first), usando uma fila de prioridade (`heapq`). A cada passo, expande a casa com menor heurística `h` (distância de Manhattan até a saída).

Todas as três buscas devolvem `(caminho, casas_visitadas)`, exatamente como pedido.

## Como rodar

Requer apenas Python 3.8+ (só usa biblioteca padrão: `collections` e `heapq`).

```bash
python3 labirinto.py
```

A saída completa de uma execução está salva em [`saida.txt`](./saida.txt).

## Resultados obtidos

Para cada algoritmo, o programa desenha o labirinto com `*` marcando o caminho encontrado, e ao final monta a tabela comparativa:

| busca  | tamanho do caminho | casas visitadas |
|--------|--------------------:|-----------------:|
| DFS    | 60                   | 61                |
| BFS    | 26                   | 79                |
| Gulosa | 52                   | 54                |

### a) Por que a BFS encontrou o menor caminho e a DFS não?

A BFS avança em camadas: visita todas as casas a 1 passo do início, depois as a 2 passos, e assim por diante. Como a fila é FIFO (primeiro a entrar, primeiro a sair), a primeira vez que ela chega na saída é necessariamente pelo menor número de arestas — por isso encontrou o caminho de 26 passos.

A DFS mergulha pelo primeiro vizinho na ordem ↑ → ↓ ←. No início do labirinto, ela vai para a **direita** (a rota longa, por cima), e só volta se encontrar um beco sem saída. Como a rota longa também chega até `F`, a DFS aceita o primeiro caminho que encontra (60 passos) e nunca chega a comparar com a rota curta que descia pela coluna 0 — ela não garante o menor caminho, só *um* caminho.

### b) Em que ponto a Busca Gulosa foi induzida a um caminho inadequado por uma parede?

Logo no início, em `(0,0)`, ir para a direita `(0,1)` ou descer `(1,0)` dão o mesmo valor de heurística `h` (21), e o desempate (pela ordem de geração) favorece a direita. Seguindo pela rota de cima, a parede na coluna 4 (linhas 0 a 3) bloqueia o avanço em `(0,3)`: a busca gulosa é obrigada a descer e contornar pela esquerda, por `(2,2)`, `(4,2)`... onde o valor de `h` quase não melhora (sobe de 17 para 18 em `(2,2)`). Mesmo assim, essas casas ainda têm `h` menor do que as casas da rota de baixo que estavam esperando na fila de prioridade (`h = 21`), então a gulosa nunca "volta" para escolher a rota curta. Ela também acaba entrando no beco `(6,6)` por parecer perto da saída (`h = 10`).

Resultado: a parede fez a gulosa seguir um caminho de 52 passos — bem pior que o menor caminho (26) — ainda que tenha visitado relativamente poucas casas (54).

### c) Como o caminho é reconstruído?

Cada busca guarda, para toda casa descoberta, quem foi que a descobriu (dicionário `pai`). A lista de `visitadas` serve só para contar/estudar a ordem de exploração (inclui becos que depois foram abandonados). O caminho final é montado de trás para frente: começa na saída, sobe de `pai` em `pai` até chegar no início (cujo pai é `None`) e, no final, a lista é invertida (função `reconstruir`) para ficar do início até a saída.
