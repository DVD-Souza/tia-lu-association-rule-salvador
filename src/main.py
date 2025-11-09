from preprocessamento import gerar_dados_preprocessados
from apriori_core import apriori
from association_rule import generate_association_rules

def main():
    print("\n=== Carregando e pré-processando dataset ===")
    transacoes, transacoes_sets = gerar_dados_preprocessados()
    print(f"Total de transações: {len(transacoes)}")

    print("\n=== Executando Apriori ===")
    min_support = 0.005
    L = apriori(transacoes_sets, min_support=min_support)

    print("\n=== ITEMSETS FREQUENTES ===")
    for k, v in L.items():
        print(f"{k}-itemsets: {len(v)} encontrados")

    print("\n=== Calculando suporte dos itemsets ===")
    support_data = {}
    total_transacoes = len(transacoes_sets)
    for k_itemset, itemsets_dict in L.items():
        for itemset, count in itemsets_dict.items():
            support_data[frozenset(itemset)] = count / total_transacoes

    print("\n=== Gerando regras de associação ===")
    min_confidence = 0.005
    min_lift = 1.0
    regras = generate_association_rules(
        list(support_data.keys()),
        support_data,
        min_confidence=min_confidence,
        min_lift=min_lift
    )

    print(f"\nQuantidade total de itemsets considerados: {len(support_data)}")
    print(f"Total de regras geradas: {len(regras)}")

    print("\n=== TOP 15 regras por maior confiança ===")
    regras_ordenadas = sorted(regras, key=lambda x: x['confidence'], reverse=True)
    for i, r in enumerate(regras_ordenadas[:15], start=1):
        antecedent = ', '.join(r['antecedent'])
        consequent = ', '.join(r['consequent'])
        print(f"{i}. {antecedent} -> {consequent} | suporte={r['support']:.4f} | "
              f"conf={r['confidence']:.4f} | lift={r['lift']:.4f}")

if __name__ == "__main__":
    main()
