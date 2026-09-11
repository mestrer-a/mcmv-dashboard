"""Agregações exploratórias das mesmas operações usadas nos gráficos originais.

Não publica microdados. Mantém o filtro de programas do processamento original.
Valores ausentes de subsídio não são imputados como zero nas novas médias.
"""
import json
import zipfile
from pathlib import Path

import pandas as pd

from process_subsidio_medio_faixa import PROGRAMA_NORMALIZACAO, PROGRAMAS_NAO_MCMV

ROOT = Path(__file__).resolve().parents[1]
COLS_SUB = ["vlr_subsidio_desconto_fgts", "vlr_subsidio_desconto_ogu",
            "vlr_subsidio_equilíbrio_fgts", "vlr_subsidio_equilíbrio_ogu"]


def agregar(chunk):
    chunk = chunk.copy()
    programa = chunk.txt_programa_fgts.replace(PROGRAMA_NORMALIZACAO)
    chunk = chunk.loc[~programa.isin(PROGRAMAS_NAO_MCMV)].copy()
    chunk["fonte"] = programa.loc[chunk.index].eq("Fundo Social").map({True: "Fundo Social", False: "FGTS"})
    chunk["ano"] = pd.to_datetime(chunk.data_assinatura_financiamento, format="ISO8601", errors="coerce").dt.year
    if chunk.ano.isna().any():
        raise ValueError("Data ausente/inválida: revisar antes de agregar")
    chunk["ano"] = chunk.ano.astype(int)
    chunk["faixa_codigo"] = chunk.txt_compatibilidade_faixa_renda.astype("string").str.strip().fillna("Sem classificação")
    chunk.loc[~chunk.faixa_codigo.isin(["1", "2", "3", "4"]), "faixa_codigo"] = "Sem classificação"
    chunk["contratos"] = 1
    completos = chunk[COLS_SUB].notna().all(axis=1)
    chunk["contratos_subsidio_observado"] = completos.astype(int)
    chunk["subsidio_total"] = chunk[COLS_SUB].sum(axis=1).where(completos)
    chunk["subsidio_fgts"] = chunk[[COLS_SUB[0], COLS_SUB[2]]].sum(axis=1).where(completos)
    chunk["subsidio_ogu"] = chunk[[COLS_SUB[1], COLS_SUB[3]]].sum(axis=1).where(completos)
    chunk["contratos_com_subsidio"] = (chunk.subsidio_total > 0).astype(int)
    chunk["financiamento_observado"] = chunk.vlr_financiamento.notna().astype(int)
    chunk["financiamento"] = chunk.vlr_financiamento
    fields = ["contratos", "contratos_subsidio_observado", "contratos_com_subsidio",
              "financiamento_observado", "financiamento", "subsidio_total", "subsidio_fgts", "subsidio_ogu"]
    return chunk.groupby(["ano", "fonte", "faixa_codigo"], dropna=False)[fields].sum().reset_index()


def main():
    path = ROOT / "data/raw/mcmv_financ_analitico_20260724.zip"
    usecols = ["data_assinatura_financiamento", "txt_programa_fgts", "txt_compatibilidade_faixa_renda", "vlr_financiamento"] + COLS_SUB
    parts = []
    with zipfile.ZipFile(path) as z:
        with z.open("mcmv_financ_analitico_20260724.csv") as f:
            for chunk in pd.read_csv(f, sep=";", decimal=",", thousands=".", usecols=usecols,
                                     dtype={"txt_compatibilidade_faixa_renda": "string"}, chunksize=250000):
                parts.append(agregar(chunk))
    result = pd.concat(parts).groupby(["ano", "fonte", "faixa_codigo"], as_index=False).sum()
    result.to_csv(ROOT / "data/processed/exploracao_contratos.csv", index=False)
    meta = json.loads((ROOT / "data/processed/financiamento_por_fonte_ano.meta.json").read_text(encoding="utf-8"))
    meta.update(id="exploracao_contratos", titulo="Perfil e subsídios dos contratos financiados",
                bases=meta["bases"][:1], script="scripts/process_exploracao_contratos.py",
                tabela="data/processed/exploracao_contratos.csv",
                metrica="Contagem de operações e somas nominais por ano, fonte de crédito e código de faixa.")
    meta["data_acesso"] = "2026-09-11"
    meta["premissas"] = [
        "Mesma versão analítica de 24/07/2026; sem novas bases. 2026 parcial e excluído por padrão das comparações anuais.",
        "Exclui Pró-Cotista e Faixa Estendida com a mesma normalização do script original. Códigos de faixa ausentes ou desconhecidos permanecem em Sem classificação.",
        "Faixas 1 a 4 são rótulos exploratórios dos códigos: correspondência inferida no projeto, ainda sem confirmação no dicionário. Não demonstram migração de renda por si só; regras e tetos variam no tempo.",
        "Subsídio registrado = desconto FGTS + equilíbrio FGTS + desconto OGU + equilíbrio OGU. A fonte de subsídio é distinta da fonte do crédito.",
        "Médias usam apenas operações com as quatro rubricas de subsídio preenchidas; ausente não é zero. Contagem total e cobertura são disponibilizadas.",
        "Cada linha representa uma operação, não necessariamente uma pessoa ou unidade única. Apenas contratos financiados; FAR e demais empreendimentos subsidiados ficam fora.",
        "Médias ponderadas: soma dos valores / número de operações observadas, nunca média simples de médias. Valores nominais, sem inferir crescimento real ou causalidade.",
        "Subsídio registrado não mensura o custo econômico completo nem um subsídio implícito estimado contra taxa de mercado."
    ]
    (ROOT / "data/processed/exploracao_contratos.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Geradas {len(result)} linhas agregadas; {result.contratos.sum():,} contratos")


if __name__ == "__main__":
    main()
