"""
Gráfico 4 — Taxa de formalização (% com carteira) ao longo do tempo.

Fonte: PNAD Contínua trimestral, tabela SIDRA 4097 (ver
scripts/download_pnad_formalizacao.py e SOURCES.md).

Métrica escolhida: "taxa de formalização relevante ao FGTS" — não é o
indicador genérico mais comumente citado na mídia (% apenas do setor
PRIVADO com carteira). É definida como:

    (empregado setor privado c/ carteira
     + trabalhador doméstico c/ carteira
     + empregado setor público c/ carteira, excl. militar/estatutário)
    / total de pessoas ocupadas

Essa escolha segue a lógica da própria dissertação: FGTS incide sobre
esses três grupos quando "com carteira" (o trabalhador doméstico passou
a ter FGTS obrigatório em 2015, Emenda Constitucional das Domésticas);
não incide sobre estatutários/militares, empregadores, conta própria ou
trabalhador familiar auxiliar. Por isso o denominador é o total de
ocupados (toda a força de trabalho), não só os "empregados" — mostra
quanto da força de trabalho total contribui, efetivamente, para o FGTS.

Uma segunda série (mais estreita, o indicador comumente citado na
imprensa: só emprego privado com carteira / total de empregados
privados) é calculada em paralelo para referência/comparação.
"""
import json
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

RAW_FILE = RAW_DIR / "pnad_4097_posicao_ocupacao.json"

# Códigos de categoria (classificação 11913) — ver metadados da tabela 4097.
COD_TOTAL = "96165"
COD_PRIVADO_TOTAL = "31721"
COD_PRIVADO_COM_CARTEIRA = "31722"
COD_PRIVADO_SEM_CARTEIRA = "31723"
COD_DOMESTICO_COM_CARTEIRA = "31725"
COD_PUBLICO_COM_CARTEIRA = "31728"


def main():
    registros = json.loads(RAW_FILE.read_text(encoding="utf-8"))[1:]  # pula cabeçalho
    df = pd.DataFrame(registros)
    df["valor_mil_pessoas"] = pd.to_numeric(df["V"], errors="coerce")
    df["trimestre_codigo"] = df["D3C"]
    df["categoria_codigo"] = df["D4C"]

    pivot = df.pivot(index="trimestre_codigo", columns="categoria_codigo", values="valor_mil_pessoas")

    resultado = pd.DataFrame(index=pivot.index)
    resultado["total_ocupados"] = pivot[COD_TOTAL]
    resultado["com_carteira_fgts"] = (
        pivot[COD_PRIVADO_COM_CARTEIRA].fillna(0)
        + pivot[COD_DOMESTICO_COM_CARTEIRA].fillna(0)
        + pivot[COD_PUBLICO_COM_CARTEIRA].fillna(0)
    )
    resultado["taxa_formalizacao_fgts"] = resultado["com_carteira_fgts"] / resultado["total_ocupados"]

    # série de referência: % só do setor privado com carteira, comumente citada na mídia
    resultado["taxa_formalizacao_privado_only"] = pivot[COD_PRIVADO_COM_CARTEIRA] / pivot[COD_PRIVADO_TOTAL]

    resultado = resultado.reset_index()
    resultado["ano"] = resultado["trimestre_codigo"].str[:4].astype(int)
    resultado["trimestre"] = resultado["trimestre_codigo"].str[4:].astype(int)

    resultado = resultado.sort_values("trimestre_codigo")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "formalizacao_pnad.csv"
    resultado.to_csv(out_path, index=False)
    print(f"Salvo em {out_path}")
    print(resultado.tail(12).to_string(index=False))


if __name__ == "__main__":
    main()
