"""
Dashboard da dissertação — MCMV x FGTS.

Cada gráfico é lido de data/processed/<nome>.csv, com uma ficha de
proveniência em data/processed/<nome>.meta.json (fonte, link, organização
responsável e premissas de limpeza) renderizada ANTES do gráfico. Nenhum
gráfico aparece sem essa ficha — é o requisito de transparência do projeto.
"""
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"

# Paleta categórica validada (dataviz skill) — ordem fixa, nunca ciclada.
COR_FGTS = "#2a78d6"          # slot 1 azul
COR_OGU = "#eb6834"           # slot 2 laranja
COR_FUNDO_SOCIAL = "#1baf7a"  # slot 3 água

st.set_page_config(page_title="MCMV x FGTS — Dissertação", layout="wide")


def carregar_meta(nome: str) -> dict:
    with open(PROCESSED_DIR / f"{nome}.meta.json", encoding="utf-8") as f:
        return json.load(f)


def carregar_tabela(nome: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / f"{nome}.csv")


def render_ficha_proveniencia(meta: dict) -> None:
    """Bloco de transparência exibido antes de qualquer gráfico: fonte, link,
    organização responsável e por que esta é a versão/base correta."""
    with st.container(border=True):
        st.markdown(f"**Fonte:** {meta['organizacao']}")
        st.caption(meta["organizacao_descricao"])
        st.markdown(f"**Catálogo:** [{meta['portal_catalogo']}]({meta['portal_catalogo']})")
        st.markdown(f"**Data de acesso:** {meta['data_acesso']}")

        st.markdown("**Bases utilizadas:**")
        for base in meta["bases"]:
            st.markdown(
                f"- *{base['nome']}* — nível: {base['nivel']}, {base['tamanho']}\n"
                f"  · usada para: {base['usada_para']}\n"
                f"  · [{base['url']}]({base['url']})"
            )

        with st.expander("Por que esta é a base correta (frente a outras versões/níveis)"):
            st.write(meta["por_que_essa_versao"])

        with st.expander("Métrica e premissas de limpeza aplicadas"):
            st.markdown(f"**Métrica:** {meta['metrica']}")
            for p in meta["premissas"]:
                st.markdown(f"- {p}")

        st.caption(
            f"Script de processamento: `{meta['script']}` · "
            f"Tabela: `{meta['tabela']}`"
        )


def grafico_financiamento_fonte_ano() -> None:
    nome = "financiamento_por_fonte_ano"
    meta = carregar_meta(nome)
    df = carregar_tabela(nome)

    st.subheader(meta["titulo"])
    render_ficha_proveniencia(meta)

    df = df.copy()
    df["valor_bi"] = df["valor_total_financiado"] / 1e9
    df["ano_em_curso"] = df["ano"] == df["ano"].max()

    ordem_fonte = ["FGTS", "OGU", "Fundo Social"]
    escala_cor = alt.Scale(domain=ordem_fonte, range=[COR_FGTS, COR_OGU, COR_FUNDO_SOCIAL])

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("ano:O", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(
                "valor_bi:Q",
                title="R$ bilhões (valores correntes)",
                stack="zero",
            ),
            color=alt.Color("fonte:N", scale=escala_cor, sort=ordem_fonte, title="Fonte"),
            opacity=alt.condition(alt.datum.ano_em_curso, alt.value(0.55), alt.value(1.0)),
            order=alt.Order("fonte:N", sort="ascending"),
            tooltip=[
                alt.Tooltip("ano:O", title="Ano"),
                alt.Tooltip("fonte:N", title="Fonte"),
                alt.Tooltip("valor_bi:Q", title="R$ bilhões", format=",.1f"),
            ],
        )
        .properties(height=420)
        .configure_axis(gridColor="#e1e0d9", domainColor="#c3c2b7")
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(chart, use_container_width=True)
    st.caption(
        f"Barra mais clara = {int(df['ano'].max())}, ano em curso (dado parcial até a data de acesso)."
    )

    with st.expander("Ver tabela tidy"):
        tabela_wide = df.pivot(index="ano", columns="fonte", values="valor_total_financiado")
        tabela_wide = (tabela_wide / 1e9).round(1)[ordem_fonte]
        st.dataframe(tabela_wide.astype(object).where(tabela_wide.notna(), "–"), use_container_width=True)


def main():
    st.title("Custo do déficit habitacional: MCMV e a sustentabilidade do FGTS")
    st.caption("Dissertação — Mestrado Profissional em Economia e Finanças, FGV EPGE")

    grafico_financiamento_fonte_ano()


if __name__ == "__main__":
    main()
