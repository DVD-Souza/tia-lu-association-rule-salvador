from itertools import combinations
from typing import List, Dict, Set, FrozenSet, Tuple

# Tipo de dado para representar uma regra de associação
AssociationRule = Dict[str, object]

# 🔹 Função 1: Geração de pares antecedente → consequente
def generate_candidate_rules(itemset: FrozenSet[str]) -> List[Tuple[Set[str], Set[str]]]:
    """
    Gera todas as combinações possíveis de regras A → B a partir de um itemset frequente.
    Para cada subconjunto não vazio A, define B = itemset - A.
    """ 
    rules = []
    items = list(itemset)
    for i in range(1, len(items)):
        for antecedent in combinations(items, i):
            antecedent = set(antecedent)
            consequent = set(items) - antecedent
            if consequent:
                rules.append((antecedent, consequent))
    return rules

# 🔹 Função 2: Cálculo da confiança
def calculate_confidence(support_data: Dict[FrozenSet[str], float],
                         antecedent: Set[str],
                         consequent: Set[str]) -> float:
    """
    Calcula a confiança da regra A → B.
    Fórmula: suporte(A ∪ B) / suporte(A)
    """
    union = frozenset(antecedent | consequent)
    return support_data[union] / support_data[frozenset(antecedent)]

# 🔹 Função 3: Cálculo do lift
def calculate_lift(support_data: Dict[FrozenSet[str], float],
                   antecedent: Set[str],
                   consequent: Set[str]) -> float:
    """
    Calcula o lift da regra A → B.
    Fórmula: confiança / suporte(B)
    """
    confidence = calculate_confidence(support_data, antecedent, consequent)
    return confidence / support_data[frozenset(consequent)]

# 🔹 Função 4: Geração de regras válidas com métricas
def generate_association_rules(frequent_itemsets: List[FrozenSet[str]],
                               support_data: Dict[FrozenSet[str], float],
                               min_confidence: float = 0.3,
                               min_lift: float = 1.0) -> List[AssociationRule]:
    """
    Gera regras de associação a partir dos itemsets frequentes.
    Filtra regras com confiança e lift acima dos thresholds definidos.
    """
    
    rules = []
    for itemset in frequent_itemsets:
        if len(itemset) < 2:
            continue  # Não há regras possíveis com menos de 2 itens
        print("gerando regras, itemset:", itemset)
        for antecedent, consequent in generate_candidate_rules(itemset):
            conf = calculate_confidence(support_data, antecedent, consequent)
            lift = calculate_lift(support_data, antecedent, consequent)
            print(antecedent, "->", consequent, "SUP_ante:", support_data[frozenset(antecedent)], "SUP_cons:", support_data[frozenset(consequent)], "SUP_union:", support_data[frozenset(antecedent | consequent)], "CONF:", conf, "LIFT:", lift)
            if conf >= min_confidence and lift >= min_lift:
                print("RULE", antecedent, "->", consequent, "SUP:", support_data[frozenset(itemset)], "CONF:", conf, "LIFT:", lift)
                rules.append({
                    'antecedent': antecedent,
                    'consequent': consequent,
                    'support': support_data[frozenset(itemset)],
                    'confidence': conf,
                    'lift': lift
                })
    return rules

