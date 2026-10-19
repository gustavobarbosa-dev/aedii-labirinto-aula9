# ============================================================
# AEDII - Aula 09 - Atividade: a saída do labirinto
# DFS, BFS e busca gulosa (greedy best-first) em um labirinto
# Cada casa livre é um vértice; casas livres vizinhas são ligadas por uma aresta.
# ============================================================

from collections import deque   # deque = fila eficiente (popleft tira da frente em O(1)) - usada na BFS
import heapq                    # heapq = fila de prioridade (sai sempre o menor valor) - usada na gulosa

# ------------------------------------------------------------
# 1) O MEU LABIRINTO (12 x 12, bem maior que o exemplo 4 x 4)
#    I = início | F = fim | # = parede | . = casa livre
# ------------------------------------------------------------
labirinto = [
    "I...#.......",   # linha 0  -> rota LONGA começa aqui (cima/direita)
    ".##.#.#####.",   # linha 1
    ".#..#.#...#.",   # linha 2
    ".#.##.#.#.#.",   # linha 3
    ".#....#.#...",   # linha 4  -> trechos que a busca precisa percorrer e depois abandonar (becos)
    ".######.####",   # linha 5
    ".#......#...",   # linha 6  -> beco sem saída em (6,2)...(6,6)
    ".#.####.#.#.",   # linha 7
    "...#....#.#.",   # linha 8
    ".###.####.#.",   # linha 9
    ".#...#....#.",   # linha 10
    "...#...##..F",   # linha 11 -> a saída F fica no canto inferior direito
]
# Requisitos da atividade atendidos:
#  - 12x12 (>= 10x10) com a notação I F # .
#  - duas rotas até F: uma curta (descendo pela coluna 0) e outra longa (por cima, à direita)
#  - vários becos sem saída para a busca precisar voltar
#  - a rota longa fica do lado "cima/direita", que é o que a DFS tenta primeiro

# ------------------------------------------------------------
# 2) FUNÇÕES DO PROFESSOR (reaproveitadas SEM alterar)
# ------------------------------------------------------------

# Procura o símbolo ('I' ou 'F') no labirinto e devolve a posição como (linha, coluna)
def achar(lab, simbolo):
    for i, linha in enumerate(lab):          # percorre as linhas com seu índice i
        if simbolo in linha:                 # se o símbolo está nesta linha...
            return (i, linha.index(simbolo)) # ...devolve (linha, coluna onde ele está)

inicio = achar(labirinto, 'I')   # posição de partida -> (0, 0)
saida = achar(labirinto, 'F')    # posição da saída   -> (11, 11)

# Ordem em que os vizinhos são testados: ↑ → ↓ ←  (a DFS segue exatamente essa ordem)
DIRECOES = [(-1, 0), (0, 1), (1, 0), (0, -1)]

# Diz se a casa (i, j) existe dentro do labirinto e não é parede
def livre(lab, i, j):
    dentro = 0 <= i < len(lab) and 0 <= j < len(lab[0])  # está dentro dos limites da grade?
    return dentro and lab[i][j] != '#'                   # e não é parede?

# Transforma o labirinto num grafo: dicionário {casa: [casas vizinhas livres]}
def montar_grafo(lab):
    grafo = {}                                    # dicionário vazio (lista de adjacência)
    for i in range(len(lab)):                     # para cada linha
        for j in range(len(lab[0])):              # para cada coluna
            if not livre(lab, i, j):              # se for parede, não vira vértice
                continue
            grafo[(i, j)] = []                    # cria o vértice com lista de vizinhos vazia
            for di, dj in DIRECOES:               # testa cima, direita, baixo, esquerda
                if livre(lab, i + di, j + dj):    # se o vizinho é uma casa livre...
                    grafo[(i, j)].append((i + di, j + dj))  # ...cria a aresta
    return grafo

# Desenha o labirinto marcando o caminho com '*' (não sobrescreve I nem F)
def desenhar(lab, caminho):
    grade = [list(linha) for linha in lab]        # copia o labirinto como matriz de caracteres
    for i, j in caminho:                          # para cada casa do caminho
        if grade[i][j] == '.':                    # só marca se for casa livre comum
            grade[i][j] = '*'
    for linha in grade:                           # imprime linha por linha
        print(''.join(linha))

grafo = montar_grafo(labirinto)   # monta o grafo uma única vez

# ------------------------------------------------------------
# 3) RECONSTRUÇÃO DO CAMINHO (resposta da pergunta "c")
#    Cada busca guarda em 'pai' quem descobriu cada casa: pai[w] = v.
#    Do fim, voltamos pai por pai até o início e invertemos a lista.
# ------------------------------------------------------------
def reconstruir(pai, saida):
    caminho = []                      # lista que será preenchida de trás para frente
    v = saida                         # começa na saída
    while v is not None:              # o início tem pai None -> aí paramos
        caminho.append(v)             # guarda a casa atual
        v = pai[v]                    # sobe para a casa que a descobriu
    return caminho[::-1]              # inverte: agora vai do início até a saída

# ------------------------------------------------------------
# 4) DFS - busca em profundidade (estrutura: pilha = a própria recursão)
#    Cada busca devolve (caminho, casas_visitadas)
# ------------------------------------------------------------
def dfs(grafo, inicio, saida):
    pai = {inicio: None}              # quem descobriu cada casa; também serve de "visitados"
    visitadas = []                    # ordem em que as casas foram visitadas (para contar)

    def visitar(v):                   # função recursiva: avança o mais fundo possível
        visitadas.append(v)           # registra a visita
        if v == saida:                # chegou na saída?
            return True               # avisa quem chamou para parar tudo
        for w in grafo[v]:            # tenta os vizinhos na ordem de DIRECOES
            if w not in pai:          # só vai se ainda não foi descoberto
                pai[w] = v            # guarda que v descobriu w
                if visitar(w):        # desce em w; se achou a saída...
                    return True       # ...propaga o "achei" para cima
        return False                  # beco sem saída: volta para a casa anterior (backtracking)

    visitar(inicio)                   # começa a busca no início
    return reconstruir(pai, saida), visitadas

# ------------------------------------------------------------
# 5) BFS - busca em largura (estrutura: fila)
# ------------------------------------------------------------
def bfs(grafo, inicio, saida):
    pai = {inicio: None}              # descobertos (e quem descobriu cada um)
    visitadas = []                    # ordem em que as casas saíram da fila
    fila = deque([inicio])            # fila começa só com o início
    while fila:                       # enquanto houver casas para explorar
        v = fila.popleft()            # tira da FRENTE: o primeiro que entrou é o primeiro a sair
        visitadas.append(v)           # registra a visita
        if v == saida:                # chegou na saída?
            break                     # pode parar: já temos o menor caminho
        for w in grafo[v]:            # olha todos os vizinhos
            if w not in pai:          # ainda não descoberto?
                pai[w] = v            # marca ao ENTRAR na fila (evita entrar duas vezes)
                fila.append(w)        # coloca no FIM da fila
    return reconstruir(pai, saida), visitadas

# ------------------------------------------------------------
# 6) BUSCA GULOSA - greedy best-first (estrutura: fila de prioridade)
# ------------------------------------------------------------
def h(v, saida):                      # heurística: distância de Manhattan até a saída
    return abs(v[0] - saida[0]) + abs(v[1] - saida[1])   # linhas + colunas que faltam (ignora paredes)

def gulosa(grafo, inicio, saida):
    pai = {inicio: None}                       # descobertos e seus pais
    visitadas = []                             # ordem das casas expandidas
    fronteira = [(h(inicio, saida), inicio)]   # fila de prioridade: (valor de h, casa)
    while fronteira:                           # enquanto houver candidatos
        _, v = heapq.heappop(fronteira)        # tira o candidato com MENOR h
        visitadas.append(v)                    # registra a visita
        if v == saida:                         # chegou na saída?
            break
        for w in grafo[v]:                     # olha os vizinhos
            if w not in pai:                   # ainda não descoberto?
                pai[w] = v                     # guarda o pai
                heapq.heappush(fronteira, (h(w, saida), w))  # entra na fila com prioridade = h
    return reconstruir(pai, saida), visitadas

# ------------------------------------------------------------
# 7) EXECUÇÃO: desenhar os três caminhos e montar a tabela
# ------------------------------------------------------------
resultados = []                                          # guardará (nome, passos, casas visitadas)
for nome, busca in [("DFS", dfs), ("BFS", bfs), ("Gulosa", gulosa)]:
    caminho, visitadas = busca(grafo, inicio, saida)     # roda a busca
    print(f"--- {nome} ---")
    desenhar(labirinto, caminho)                         # desenha o caminho encontrado
    print()
    resultados.append((nome, len(caminho) - 1, len(visitadas)))  # passos = casas do caminho - 1

print(f"{'busca':<8}{'tamanho do caminho':>20}{'casas visitadas':>18}")   # cabeçalho da tabela
for nome, passos, visitadas in resultados:
    print(f"{nome:<8}{passos:>20}{visitadas:>18}")

# ============================================================
# 8) RESPOSTAS PARA A CORREÇÃO ORAL
# ============================================================
# a) Por que a BFS achou o menor caminho e a DFS não?
#    A BFS avança em camadas: visita todas as casas a 1 passo do início, depois as
#    a 2 passos, e assim por diante. Como a fila é "primeiro a entrar, primeiro a sair",
#    a primeira vez que ela chega na saída é pelo menor número de arestas (26 passos).
#    A DFS mergulha pelo primeiro vizinho na ordem ↑ → ↓ ←. No início ela vai para a
#    DIREITA (rota longa, por cima) e só volta se esbarrar em beco sem saída. Como a rota
#    longa chega na saída, a DFS aceita o primeiro caminho que encontra (60 passos),
#    sem comparar com a rota curta que descia pela coluna 0.
#
# b) Onde a gulosa foi enganada por uma parede?
#    No início (0,0): ir para a direita (0,1) ou descer (1,0) dão o mesmo h (21), e ela
#    desempata pela direita. Na rota de cima, a parede da coluna 4 (linhas 0 a 3) bloqueia
#    o avanço em (0,3): a gulosa é obrigada a descer e voltar para a esquerda (2,2), (4,2)...
#    onde o h quase não melhora (sobe de 17 para 18 em (2,2)). Mesmo assim essas casas ainda têm h menor que o das casas da rota de
#    baixo que ficaram esperando na fila (h = 21), então ela nunca volta para escolher a rota
#    curta. Ela também entrou no beco (6,6) por parecer perto da saída (h = 10). Resultado:
#    52 passos (não é o menor), mas visitou poucas casas (54).
#
# c) Como o caminho é reconstruído?
#    Cada busca guarda, para cada casa descoberta, quem a descobriu (dicionário 'pai').
#    A lista de visitadas serve só para contar/estudar a ordem; ela inclui becos. O caminho
#    é feito de trás para frente: começa na saída, sobe de pai em pai até o início
#    (cujo pai é None) e depois inverte a lista (função reconstruir).
