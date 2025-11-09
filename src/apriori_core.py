from itertools import combinations
from collections import Counter
import math
from typing import List, Set, FrozenSet, Dict

def gerar_candidatos(prev_frequentes: List[Set[str]]) -> Set[FrozenSet[str]]:
    """
    Gera candidatos k a partir dos itemsets frequentes de tamanho k-1.
    """
    candidatos = set()
    prev_list = list(prev_frequentes)
    for i in range(len(prev_list)):
        for j in range(i + 1, len(prev_list)):
            a = prev_list[i]
            b = prev_list[j]
            uniao = a | b
            if len(uniao) == len(a) + 1:
                candidatos.add(frozenset(uniao))
    return candidatos

def calcular_suporte(transacoes_sets: List[Set[str]], candidatos) -> Counter:
    """
    Conta quantas transações contêm cada candidato.
    Remove candidatos duplicados antes da contagem para evitar contagens infladas.
    Retorna Counter -> {frozenset(itemset): contagem}
    """
    cont = Counter()
    # garantir unicidade dos candidatos (cada candidato contado uma única vez por transação)
    candidatos_uniq = {frozenset(c) for c in candidatos}
    for t in transacoes_sets:
        for c in candidatos_uniq:
            if c.issubset(t):
                cont[c] += 1
    return cont

def filtrar_por_suporte(contagens: Dict[FrozenSet[str], int], total_transacoes: int, min_support: float = 0.05) -> Dict[FrozenSet[str], int]:
    """
    Retorna apenas os itemsets cuja contagem >= suporte mínimo absoluto.
    suporte mínimo é ceil(min_support * total_transacoes).
    """
    suporte_minimo = math.ceil(min_support * total_transacoes)
    return {itemset: count for itemset, count in contagens.items() if count >= suporte_minimo}

def apriori(transacoes_sets: List[Set[str]], min_support: float = 0.05) -> Dict[int, Dict[FrozenSet[str], int]]:
    """
    Executa o algoritmo Apriori completo.
    Retorna um dicionário {k: {frozenset(itemset): count}}
    """
    total = len(transacoes_sets)
    # construir L1 de forma única (sem duplicatas)
    itens_unicos = {frozenset([i]) for tx in transacoes_sets for i in tx}
    cont1 = calcular_suporte(transacoes_sets, itens_unicos)
    L1 = filtrar_por_suporte(cont1, total, min_support)

    L = {1: L1}
    k = 1

    while L.get(k):
        prev_frequentes = [set(x) for x in L[k].keys()]
        candidatos = gerar_candidatos(prev_frequentes)
        if not candidatos:
            break
        cont_k = calcular_suporte(transacoes_sets, candidatos)
        Lk = filtrar_por_suporte(cont_k, total, min_support)
        if not Lk:
            break
        k += 1
        L[k] = Lk

    return L