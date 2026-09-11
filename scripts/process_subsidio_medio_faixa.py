"""
Gráfico 3 — Subsídio médio por unidade e por faixa de renda.

Usa as MESMAS bases já baixadas para o Gráfico 1 (nenhum download novo):
- Base analítica (contrato a contrato): subsídio médio para Faixa 2, 3 e 4,
  identificadas por txt_compatibilidade_faixa_renda (códigos "2"/"3"/"4").
- Base MCMV Subsidiado (empreendimentos, modalidade FAR): proxy de Faixa 1,
  usando val_contratado_total / qtd_uh por empreendimento.

ATENÇÃO — duas definições diferentes de "Faixa 1" que NÃO são somadas:
1. "Faixa 1 (contratos FGTS)": contratos financiados com FGTS/FS cujo
   txt_compatibilidade_faixa_renda == "1". Segundo nota prévia do autor,
   a maior parte dos beneficiários de Faixa 1 (FAR) não passa por essa
   base — então esse número tende a subestimar a Faixa 1 real.
2. "Faixa 1 (FAR/OGU)": empreendimentos subsidiados diretamente (FAR),
   onde val_contratado_total é tratado como proxy do subsídio total por
   unidade — aproximação, não uma coluna de subsídio explícita.

Mapeamento código -> faixa NÃO está documentado no dicionário oficial
(ver data_dictionary.md) — inferido por validação estatística (renda
familiar por código bate com as faixas oficiais do CCFGTS), mas não é uma
fonte primária confirmando o mapeamento. Linhas com código vazio são
excluídas aqui (não têm faixa para rotular), sem reabrir a decisão já
tomada de não filtrar "FORA MCMV/CVA" no Gráfico 1.
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

CODIGO_PARA_FAIXA = {
    "1": "Faixa 1 (contratos FGTS)",
    "2": "Faixa 2",
    "3": "Faixa 3",
    "4": "Faixa 4 / Classe Média",
}


def processar_faixas_2_a_4() -> pd.DataFrame:
    usecols = [
        "txt_compatibilidade_faixa_renda",
        "txt_programa_fgts",
        "vlr_subsidio_desconto_fgts",
        "vlr_subsidio_desconto_ogu",
        "vlr_subsidio_equilíbrio_fgts",
        "vlr_subsidio_equilíbrio_ogu",
    ]
    soma_subsidio = {}
    contagem = {}

    with zipfile.ZipFile(ANALITICO_ZIP) as zf:
        with zf.open(ANALITICO_CSV) as f:
            reader = pd.read_csv(
                f,
                sep=";",
                decimal=",",
                thousands=".",
                usecols=usecols,
                dtype={"txt_compatibilidade_faixa_renda": "string"},
                chunksize=500_000,
                encoding="utf-8",
            )
            for chunk in reader:
                chunk["txt_programa_fgts"] = chunk["txt_programa_fgts"].map(
                    lambda p: PROGRAMA_NORMALIZACAO.get(p, p)
                )
                chunk = chunk[~chunk["txt_programa_fgts"].isin(PROGRAMAS_NAO_MCMV)]

                faixa_cod = chunk["txt_compatibilidade_faixa_renda"].str.strip()
                chunk = chunk[faixa_cod.isin(CODIGO_PARA_FAIXA.keys())]
                if chunk.empty:
                    continue
                faixa_cod = chunk["txt_compatibilidade_faixa_renda"].str.strip()

                subsidio = (
                    chunk["vlr_subsidio_desconto_fgts"].fillna(0)
                    + chunk["vlr_subsidio_desconto_ogu"].fillna(0)
                    + chunk["vlr_subsidio_equilíbrio_fgts"].fillna(0)
                    + chunk["vlr_subsidio_equilíbrio_ogu"].fillna(0)
                )
                grupo = subsidio.groupby(faixa_cod)
                for codigo, soma in grupo.sum().items():
                    soma_subsidio[codigo] = soma_subsidio.get(codigo, 0.0) + soma
                for codigo, n in grupo.count().items():
                    contagem[codigo] = contagem.get(codigo, 0) + n

    rows = []
    for codigo, faixa_label in CODIGO_PARA_FAIXA.items():
        if codigo not in contagem or contagem[codigo] == 0:
            continue
        rows.append({
            "faixa": faixa_label,
            "subsidio_medio_por_unidade": soma_subsidio[codigo] / contagem[codigo],
            "qtd_contratos": contagem[codigo],
        })
    return pd.DataFrame(rows)


def processar_faixa1_far() -> pd.DataFrame:
    with zipfile.ZipFile(SUBSIDIADO_ZIP) as zf:
        with zf.open(SUBSIDIADO_CSV) as f:
            df = pd.read_csv(
                f,
                sep=";",
                decimal=",",
                thousands=".",
                usecols=["txt_modalidade", "val_contratado_total", "qtd_uh"],
                encoding="utf-8",
            )
    far = df[df["txt_modalidade"] == "FAR"]
    total_valor = far["val_contratado_total"].sum()
    total_uh = far["qtd_uh"].sum()
    return pd.DataFrame([{
        "faixa": "Faixa 1 (FAR/OGU)",
        "subsidio_medio_por_unidade": total_valor / total_uh,
        "qtd_contratos": int(total_uh),
    }])


def main():
    print("Processando faixas 2-4 (base analítica)...")
    df_2a4 = processar_faixas_2_a_4()
    print(df_2a4.to_string(index=False))

    print("\nProcessando Faixa 1 / FAR (base subsidiado)...")
    df_far = processar_faixa1_far()
    print(df_far.to_string(index=False))

    df = pd.concat([df_far, df_2a4], ignore_index=True)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "subsidio_medio_faixa.csv"
    df.to_csv(out_path, index=False)
    print(f"\nSalvo em {out_path}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
