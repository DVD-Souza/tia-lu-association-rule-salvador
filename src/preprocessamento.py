import pandas as pd
import unicodedata
import re

CSV_PATH = "../data/vendas_dataset.csv"
    # ajuste se necessário
COLUNA_TRANSACAO = None            # se houver coluna com itens separados por vírgula, colocar o nome; senão deixar None
REMOVER_NUMEROS = True             # se False, preserva números (ex.: tamanhos)

# ---------- utilitárias simples ----------
def remover_acentos(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

# ---------- semântica de domínio ----------
MARCAS_COMUNS = ["nike", "adidas", "puma", "star", "max", "selfie", "mic"]
PALAVRAS_IRRELEVANTES = ["moda", "conjunto", "liso", "unissex", "adulto", "infantil"]
SINONIMOS = {
    "camiseta": "camisa",
    "blusa": "camisa",
    "tennis": "tenis",
    "shorts": "bermuda",
    "calças": "calca",
    "calças jeans": "calca jeans"
}

def normalizar_semantica(item: str) -> str:
    """
    Remove marcas, palavras irrelevantes, unifica sinônimos, trata plural/singular.
    """
    tokens = item.split()
    tokens_filtrados = []
    for tok in tokens:
        # remover marcas
        if tok in MARCAS_COMUNS:
            continue
        # remover palavras irrelevantes
        if tok in PALAVRAS_IRRELEVANTES:
            continue
        # unificar sinônimos
        if tok in SINONIMOS:
            tok = SINONIMOS[tok]
        # tratar plural simples (ex.: bermudas -> bermuda)
        if tok.endswith("s") and len(tok) > 3:
            tok = tok[:-1]
        tokens_filtrados.append(tok)
    return " ".join(tokens_filtrados).strip()

# ---------- normalização técnica + semântica ----------
def normalizar_item(item: str, remover_numeros: bool = REMOVER_NUMEROS) -> str:
    """Lowercase, sem acentos, opcionalmente sem números, sem símbolos extras, espaços colapsados + semântica."""
    if not isinstance(item, str):
        return ""
    s = item.strip().lower()
    s = remover_acentos(s)
    if remover_numeros:
        s = re.sub(r"\d+", "", s)
    s = re.sub(r"[^\w\s]", "", s)
    s = s.replace("_", " ")
    s = normalizar_semantica(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------- carregar transações ----------
def carregar_transacoes(csv_path: str = CSV_PATH, coluna: str = COLUNA_TRANSACAO):
    """
    Retorna lista de transacoes (cada transacao é lista de strings brutas).
    - Se 'coluna' existir: espera itens separados por vírgula nessa coluna.
    - Senão: junta todas as colunas não-nulas por linha (cada coluna = item).
    """
    try:
        df = pd.read_csv(csv_path, dtype=str, keep_default_na=False, na_values=[""])
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")
    except Exception as e:
        raise RuntimeError(f"Erro ao ler CSV: {e}")

    transacoes = []
    if coluna and coluna in df.columns:
        for val in df[coluna].tolist():
            if str(val).strip() == "":
                continue
            itens = [i.strip() for i in str(val).split(",") if i.strip() != ""]
            transacoes.append(itens)
    else:
        for _, row in df.iterrows():
            itens = [str(x).strip() for x in row.tolist() if str(x).strip() != ""]
            if itens:
                transacoes.append(itens)
    return transacoes

# ---------- pré-processamento essencial ----------
def preprocessar_transacoes(transacoes_raw, remover_numeros: bool = REMOVER_NUMEROS):
    """
    Normaliza cada item e remove duplicatas dentro da mesma transação.
    Retorna: transacoes_norm (lista de listas) e transacoes_sets (lista de sets).
    """
    transacoes_norm = []
    for trans in transacoes_raw:
        itens = []
        for it in trans:
            it2 = normalizar_item(it, remover_numeros)
            if it2:
                itens.append(it2)
        # remover duplicatas mantendo ordem
        seen = set()
        itens_unicos = []
        for it in itens:
            if it not in seen:
                seen.add(it)
                itens_unicos.append(it)
        if itens_unicos:
            transacoes_norm.append(itens_unicos)
    transacoes_sets = [set(t) for t in transacoes_norm]
    return transacoes_norm, transacoes_sets

# ---------- interface que você entrega ao time ----------
def gerar_dados_preprocessados(csv_path=CSV_PATH, coluna=COLUNA_TRANSACAO, remover_numeros: bool = REMOVER_NUMEROS):
    raw = carregar_transacoes(csv_path, coluna)
    transacoes, transacoes_sets = preprocessar_transacoes(raw, remover_numeros)
    return transacoes, transacoes_sets

# ---------- teste rápido ----------
if __name__ == "__main__":
    transacoes, transacoes_sets = gerar_dados_preprocessados()
    print("Exemplo — primeiras 5 transações pré-processadas:")
    for t in transacoes[:5]:
        print(" -", t)
    print("Total de transações pré-processadas:", len(transacoes))
