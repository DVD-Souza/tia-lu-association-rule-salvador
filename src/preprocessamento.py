import pandas as pd
import unicodedata
import re

CSV_PATH = "../data/vendas_dataset.csv"
COLUNA_TRANSACAO = "descricao_produtos"  # ajuste se necessário
REMOVER_NUMEROS = True                   # True: remove tamanhos, anos, etc.
REMOVER_CORES = True                     # True: remove cores para consolidar itens

# ---------- utilitárias simples ----------
def remover_acentos(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

# ---------- semântica de domínio ----------
MARCAS_COMUNS = [
    "PIMPOLHO", "MICOL", "MICOL BABY KIDS", "MECBEE BABY", "LA MAYARA",
    "LILI LANGERIE", "NIKKO", "NIKKOMOLETOM", "BRANDILI", "KYLY", "KAMYLUS", 
    "ELIAN", "NANAI", "MINASREY", "D’VYSTEK", "MGRM", "MGRMGLUPMETAMANIA", 
    "L&D", "APOLO", "MARANDS", "MAR DE PRATA", "MARINHO", "KORTE", "REKORTE",
    "HÄOS", "HAOS", "SELENE", "BERNA BABY", "TUBARÃO", "FOLIA KIDS", "DINGA", 
    "DENGO", "BABY SOFFETE", "ZANGADINHO"
]

PALAVRAS_IRRELEVANTES = [
    "C/ UN", "C UN", "PARES", "KIT", "CONJ", "CONJUNTO", "PACOTE", "PEÇAS", 
    "REF", "REF.", "LISO", "ESTAMPADA", "MALHA", "ALGODÃO", "POLIAMIDA", "SUEDE", 
    "VISCO", "LINHO", "TACTEL", "CROPPED", "WAFFLE", "PENTEADA", "CANELADA", 
    "ELÁSTICO", "FRIA", "MANGA", "MANGA CURTA", "MANGA LONGA",
    "SHORT", "BERMUDA", "VESTIDO", "BLUSA", "REGATA", "BODY", "CALCINHA", "CUECA", 
    "SUTIÃ", "MEIA", "TOALHA", "BABY DOLL", "PIJAMA", "MACACÃO", "MACAQUITO", 
    "BONE", "BIQUINI", "SAPATINHO", "SAPATO", "MANTA", "LUVA", "FAIXA", "TIARA", 
    "UNISSEX", "MASC", "FEM", "INFANTIL", "JUVENIL", "KIDS", "ADULTO", "MINI", 
    "NEW", "TURMA", "BABY", "JUNINHO", "PAS", "PASTEL", "ROSA", "AMARELO", "VERDE",
    "BEGE", "MARINHO", "BRANCO", "OFF WHITE", "AZUL", "CINZA", "LARANJA", "VERMELHO",
    "CORAL", "SALMÃO", "ROSA SUAVE", "CARAMELO", "GEOMETRICA", "ONÇA", "TIGRE", 
    "LEÃO", "BOLINHA", "FOFINHA", "LUXUOSA", "SOFT", "INVISÍVEL", "OPACA"
]

SINONIMOS = {
    "LISO": ["SEM ESTAMPA", "BÁSICO"],
    "ESTAMPADO": ["COM ESTAMPA", "PRINT", "PADRÃO"],
    "CAMISETA": ["T-SHIRT", "TOP", "BLUSA ALGODÃO"],
    "SUTIÃ": ["TOP", "SUPORTE", "SPORT"],
    "CALCINHA": ["BOTTOM", "INFANTIL BOTTOM", "TANGA", "BOX", "BABY"],
    "CUECA": ["BOX", "INFANTIL BOX", "LISA", "ESTAMPADA", "BOXER"],
    "SHORT": ["BERMUDA", "CALÇÃO", "TACTEL", "ALGODÃO"],
    "VESTIDO": ["DRESS", "REGATA", "MALHA", "TECIDO"],
    "MACACÃO": ["JARDINEIRA", "MACAQUITO", "UV PROTECTION", "LONGO", "CURTO"],
    "MEIA": ["MEIA LISA", "MEIA COLORIDA", "MEIA POLIAMIDA", "MEIA-CALÇA", "MEIA FESTA", "MEIA INFANTIL"],
    "KIT": ["CONJUNTO", "PACOTE", "PAR"]
}

def normalizar_semantica(item: str) -> str:
    """
    Remove marcas, palavras irrelevantes, unifica sinônimos, trata plural/singular.
    """
    tokens = item.split()
    tokens_filtrados = []
    for tok in tokens:
        if tok in MARCAS_COMUNS:
            continue
        if tok in PALAVRAS_IRRELEVANTES:
            continue
        if tok in SINONIMOS:
            tok = SINONIMOS[tok]
        # tratar plural simples
        if tok.endswith("s") and len(tok) > 6 and not tok.endswith("ss"):
            tok = tok[:-1]
        tokens_filtrados.append(tok)
    return " ".join(tokens_filtrados).strip()

# ---------- normalização técnica + semântica ----------
def normalizar_item(item: str, remover_numeros: bool = REMOVER_NUMEROS, remover_cores: bool = REMOVER_CORES) -> str:
    """
    Lowercase, sem acentos, opcionalmente sem números e cores, sem símbolos extras, 
    espaços colapsados + semântica.
    """
    if not isinstance(item, str):
        return ""
    s = item.strip().lower()
    s = remover_acentos(s)
    if remover_numeros:
        s = re.sub(r"\d+", "", s)
    s = re.sub(r"[^\w\s]", "", s)
    s = s.replace("_", " ")
    s = normalizar_semantica(s)
    # remover cores se necessário
    if remover_cores:
        s_tokens = [tok for tok in s.split() if tok not in PALAVRAS_IRRELEVANTES]
        s = " ".join(s_tokens)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# ---------- carregar transações ----------
def carregar_transacoes(csv_path: str = CSV_PATH, coluna: str = COLUNA_TRANSACAO):
    """
    Retorna lista de transacoes (cada transacao é lista de strings brutas).
    - Se 'coluna' existir: espera itens separados por ';' nessa coluna.
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
            itens = [i.strip() for i in str(val).split(";") if i.strip() != ""]
            transacoes.append(itens)
    else:
        for _, row in df.iterrows():
            itens = [str(x).strip() for x in row.tolist() if str(x).strip() != ""]
            if itens:
                transacoes.append(itens)
    return transacoes

# ---------- pré-processamento essencial ----------
def preprocessar_transacoes(transacoes_raw, remover_numeros: bool = REMOVER_NUMEROS, remover_cores: bool = REMOVER_CORES):
    """
    Normaliza cada item e remove duplicatas dentro da mesma transação.
    Retorna: transacoes_norm (lista de listas) e transacoes_sets (lista de sets).
    """
    transacoes_norm = []
    for trans in transacoes_raw:
        itens = []
        for it in trans:
            it2 = normalizar_item(it, remover_numeros, remover_cores)
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

# ---------- interface principal ----------
def gerar_dados_preprocessados(csv_path=CSV_PATH, coluna=COLUNA_TRANSACAO, 
                               remover_numeros: bool = REMOVER_NUMEROS, 
                               remover_cores: bool = REMOVER_CORES):
    raw = carregar_transacoes(csv_path, coluna)
    transacoes, transacoes_sets = preprocessar_transacoes(raw, remover_numeros, remover_cores)
    return transacoes, transacoes_sets

# ---------- teste rápido ----------
if __name__ == "__main__":
    transacoes, transacoes_sets = gerar_dados_preprocessados()
    print("Exemplo — primeiras 5 transações pré-processadas:")
    for t in transacoes[:5]:
        print(" -", t)
    print("Total de transações pré-processadas:", len(transacoes))
