from itertools import combinations
from collections import Counter
import math

def gerar_candidatos(prev_frequentes):

    candidatos = set()
    prev_list = list(prev_frequentes)

    for i in range(len(prev_list)):
        for j in range(i+1, len(prev_list)):
            a = prev_list[i]
            b = prev_list[j]
            uniao = a | b
            if len(uniao) == len(a) + 1:
                candidatos.add(uniao)

    return candidatos

def calcular_suporte(transacoes_sets, candidatos):
    """
    conta quantas transações contém cada candidato
    retorna dict -> {itemset:contagem}
    """
    cont = Counter()

    for t in transacoes_sets:
        for c in candidatos:
            if c.issubset(t):
                cont[c] += 1

    return cont

def filtrar_por_suporte(contagens, total_transacoes, min_support=0.05):
    """
    retorna apenas os que atingem o suporte mínimo
    """
    suporte_minimo = math.ceil(min_support * total_transacoes)
    return {itemset:count for itemset,count in contagens.items() if count >= suporte_minimo}

def apriori(transacoes_sets, min_support=0.05):
    """
    Executa todo o Apriori até não existir mais conjuntos
    Retorna {k: {itemset:count}}
    """
    total = len(transacoes_sets)
    # L1
    cont1 = calcular_suporte(transacoes_sets, [{i} for tx in transacoes_sets for i in tx])
    L1 = filtrar_por_suporte(cont1, total, min_support)

    L = {1: L1}
    k = 1

    while L[k]:
        candidatos = gerar_candidatos([frozenset(x) for x in L[k].keys()])
        cont_k = calcular_suporte(transacoes_sets, candidatos)
        Lk = filtrar_por_suporte(cont_k, total, min_support)

        if not Lk:
            break

        k += 1
        L[k] = Lk

    return L
