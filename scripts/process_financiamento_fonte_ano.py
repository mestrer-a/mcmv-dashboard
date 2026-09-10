"""
Gráfico 1 — Financiamento do MCMV por fonte e por ano (FGTS x OGU x Fundo Social).

Métrica: valor total financiado/contratado (fluxo bruto de recursos aplicados),
não o subsídio. Decisão registrada em conversa com o autor em 2026-09-10.

Fontes (ver SOURCES.md para URL e data de acesso completas):
- FGTS e Fundo Social: base analítica de contratos financiados com FGTS/FS
  (nível de contrato, ~7,85 milhões de linhas), campo vlr_financiamento,
  separado por txt_programa_fgts normalizado.
- OGU: base MCMV Subsidiado (Empreendimentos), campo val_contratado_total.
  Esta base não tem coluna de fonte orçamentária explícita — é tratada como
  proxy de OGU por ser o universo de empreendimentos subsidiados fora do
  financiamento direto com FGTS (ver ressalva em data_dictionary.md).

Premissas de limpeza (confirmadas com o autor em 2026-09-10):
1. Normalização de grafia de txt_programa_fgts (dado do governo tem grafias
   duplicadas do mesmo programa, ex.: "Apoio à producao" / "Apoio à Produção").
2. Exclusão de contratos não-MCMV pelo nome do programa: Pró-Cotista (e
   variantes "PF - Urbano/PMCMV/PMCMV-Construção") e Faixa Estendida.
3. SEM filtro adicional por txt_compatibilidade_faixa_renda: essa coluna vem
   como código numérico (1/2/3/4/vazio) sem tabela de correspondência
   confirmada em fonte oficial. Uma validação interna (renda familiar por
   código bate com as faixas oficiais do CCFGTS) sugeriu fortemente que
   código vazio = "FORA MCMV/CVA", mas o autor optou por não aplicar esse
   filtro ainda — decisão de 2026-09-10, a revisitar.
"""
import zipfile
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

ANALITICO_ZIP = RAW_DIR / "mcmv_financ_analitico_20260724.zip"
ANALITICO_CSV = "mcmv_financ_analitico_20260724.csv"
SUBSIDIADO_ZIP = RAW_DIR / "mcmv_subsidiado_202606302.zip"
SUBSIDIADO_CSV = "mcmv_subsidiado_20260630.csv"

# Normalização de grafias do mesmo programa observadas nos dados reais.
PROGRAMA_NORMALIZACAO = {
    "Apoio à producao": "Apoio à Produção",
    "Apoio à Produção": "Apoio à Produção",
    "Carta de Crédito - Individual": "Carta de Crédito Individual",
    "Carta de crédito Individual": "Carta de Crédito Individual",
    "Carta de Crédito Associativo": "Carta de Crédito Associativo",
    "Classe Média": "Classe Média",
    "Fundo Social": "Fundo Social",
    "Op. Especiais - Faixa Estendida": "Faixa Estendida",
    "Pró-Cotista": "Pró-Cotista",
    "Pró-Cotista - PF - Urbano": "Pró-Cotista",
    "Pró-Cotista - PF - PMCMV": "Pró-Cotista",
    "Pró-Cotista - PF - PMCMV/Construção": "Pró-Cotista",
}

PROGRAMAS_NAO_MCMV = {"Pró-Cotista", "Faixa Estendida"}


def processar_fgts_e_fundo_social() -> pd.DataFrame:
    """Agrega vlr_financiamento por ano x fonte (FGTS / Fundo Social) a partir
    da base analítica, processando em chunks (arquivo tem ~1,24 GB descompactado)."""
    usecols = ["data_assinatura_financiamento", "vlr_financiamento", "txt_programa_fgts"]
    totals = {}  # (ano, fonte) -> soma

    with zipfile.ZipFile(ANALITICO_ZIP) as zf:
        with zf.open(ANALITICO_CSV) as f:
            reader = pd.read_csv(
                f,
                sep=";",
                decimal=",",
                thousands=".",
                usecols=usecols,
                parse_dates=["data_assinatura_financiamento"],
                chunksize=500_000,
                encoding="utf-8",
            )
            for chunk in reader:
                chunk["txt_programa_fgts"] = chunk["txt_programa_fgts"].map(
                    lambda p: PROGRAMA_NORMALIZACAO.get(p, p)
                )
                chunk = chunk[~chunk["txt_programa_fgts"].isin(PROGRAMAS_NAO_MCMV)]
                chunk["ano"] = chunk["data_assinatura_financiamento"].dt.year
                chunk["fonte"] = chunk["txt_programa_fgts"].apply(
                    lambda p: "Fundo Social" if p == "Fundo Social" else "FGTS"
                )
                agg = chunk.groupby(["ano", "fonte"])["vlr_financiamento"].sum()
                for (ano, fonte), valor in agg.items():
                    totals[(ano, fonte)] = totals.get((ano, fonte), 0.0) + valor

    df = pd.DataFrame(
        [(ano, fonte, valor) for (ano, fonte), valor in totals.items()],
        columns=["ano", "fonte", "valor_total_financiado"],
    )
    return df


def processar_ogu() -> pd.DataFrame:
    """Agrega val_contratado_total por ano a partir da base MCMV Subsidiado (proxy de OGU)."""
    with zipfile.ZipFile(SUBSIDIADO_ZIP) as zf:
        with zf.open(SUBSIDIADO_CSV) as f:
            df = pd.read_csv(
                f,
                sep=";",
                decimal=",",
                thousands=".",
                usecols=["dt_assinatura", "val_contratado_total"],
                parse_dates=["dt_assinatura"],
                dayfirst=True,
                encoding="utf-8",
            )
    df["ano"] = df["dt_assinatura"].dt.year
    agg = df.groupby("ano")["val_contratado_total"].sum().reset_index()
    agg["fonte"] = "OGU"
    agg = agg.rename(columns={"val_contratado_total": "valor_total_financiado"})
    return agg[["ano", "fonte", "valor_total_financiado"]]


def main():
    print("Processando base analítica (FGTS + Fundo Social)...")
    df_fgts = processar_fgts_e_fundo_social()
    print(f"  -> {len(df_fgts)} linhas ano x fonte")

    print("Processando base subsidiado (OGU)...")
    df_ogu = processar_ogu()
    print(f"  -> {len(df_ogu)} linhas ano x fonte")

    df = pd.concat([df_fgts, df_ogu], ignore_index=True)
    df = df.sort_values(["ano", "fonte"]).reset_index(drop=True)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "financiamento_por_fonte_ano.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSalvo em {out_path}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
