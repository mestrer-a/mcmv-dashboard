"""
Dashboard da dissertação — MCMV x FGTS.

Navegação por ABA = 1 base de dados oficial (não por gráfico — um gráfico
pode consumir mais de uma base, mas cada aba concentra as bases de uma
mesma organização/fonte, seguindo o levantamento original do projeto).

Dentro de cada aba: contexto da organização responsável, depois cada
gráfico daquela aba com sua própria ficha de proveniência (fonte, link,
data de acesso, por que é a versão correta, premissas de limpeza) ANTES do
gráfico. Nenhum gráfico aparece sem essa ficha.
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

# ---------------------------------------------------------------------------
# Registro de abas = bases de dados (agrupamento do item 5 do plano original).
# Cada aba lista os ids dos gráficos (em data/processed/<id>.csv/.meta.json)
# que pertencem a ela. Aba sem gráfico pronto mostra um card "em construção".
# ---------------------------------------------------------------------------
ABAS = [
    {
        "label": "Ministério das Cidades — PMCMV",
        "organizacao": "Ministério das Cidades — Secretaria Nacional de Habitação (SNH)",
        "organizacao_descricao": (
            "Órgão federal responsável por manter e publicar as bases oficiais de "
            "contratos e empreendimentos do Programa Minha Casa, Minha Vida."
        ),
        "portal": "https://dadosabertos.cidades.gov.br/dataset/dados-do-programa-minha-casa-minha-vida-pmcmv",
        "graficos": ["financiamento_por_fonte_ano", "subsidio_medio_faixa"],
        "pendente": [],
    },
    {
        "label": "FGTS — CCFGTS / Demonstrações Financeiras",
        "organizacao": "Conselho Curador do FGTS (CCFGTS) e Agente Operador (Caixa Econômica Federal)",
        "organizacao_descricao": (
            "Orçamento do FGTS por rubrica e as Demonstrações Financeiras/Contábeis "
            "do fundo — arrecadação, saques, remuneração das contas, amortizações e "
            "receitas financeiras. Complementado pelo Acórdão TCU 270/2026."
        ),
        "portal": None,
        "graficos": [],
        "pendente": [
            "Gráfico 2 — Composição do orçamento do FGTS por rubrica, últimos 5 anos",
            "Gráfico 6 — Arrecadação x saques do FGTS",
        ],
    },
    {
        "label": "Emprego formal — PNAD / Caged",
        "organizacao": "IBGE (PNAD Contínua) e Ministério do Trabalho e Emprego (Novo Caged)",
        "organizacao_descricao": (
            "Taxa de formalização do emprego (% de ocupados com carteira assinada) — "
            "âncora da sustentabilidade do FGTS no longo prazo, hoje ausente do dashboard."
        ),
        "portal": None,
        "graficos": [],
        "pendente": [
            "Gráfico 4 — Taxa de formalização (% com carteira) ao longo do tempo",
        ],
    },
    {
        "label": "Déficit habitacional — FJP",
        "organizacao": "Fundação João Pinheiro (FJP)",
        "organizacao_descricao": (
            "Déficit habitacional total, por componente e por faixa (onde houver). "
            "Usado como dado de entrada — não recalculado."
        ),
        "portal": None,
        "graficos": [],
        "pendente": [
            "Gráfico 5 — Custo de acabar com o déficit hoje, por componente/faixa "
            "(com e sem ônus de aluguel)",
        ],
    },
    {
        "label": "Custo de construção — SINAPI / INCC",
        "organizacao": "IBGE (SINAPI) e FGV/IBRE (INCC)",
        "organizacao_descricao": "Índices de custo de construção civil, usados como referência complementar.",
        "portal": None,
        "graficos": [],
        "pendente": [
            "Referência para o Gráfico 5 — custo de construção por m² usado na "
            "estimativa do custo de novas unidades no cálculo do déficit",
        ],
    },
]


def carregar_meta(nome: str) -> dict:
    with open(PROCESSED_DIR / f"{nome}.meta.json", encoding="utf-8") as f:
        return json.load(f)


def carregar_tabela(nome: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / f"{nome}.csv")


def render_ficha_proveniencia(meta: dict) -> None:
    """Linha resumo (fonte + data) sempre visível; tudo o mais — bases, links,
    justificativa da versão, premissas — recolhido num único expansor."""
    st.caption(f"📊 Fonte: {meta['organizacao']} · dados de {meta['data_acesso']}")

    with st.expander("Ver bases, links e premissas"):
        st.markdown("**Bases utilizadas:**")
        for base in meta["bases"]:
            st.markdown(
                f"- *{base['nome']}* — nível: {base['nivel']}, {base['tamanho']}\n"
                f"  · usada para: {base['usada_para']}\n"
                f"  · [{base['url']}]({base['url']})"
            )

        st.markdown("**Por que esta é a base correta (frente a outras versões/níveis):**")
        st.write(meta["por_que_essa_versao"])

        st.markdown(f"**Métrica:** {meta['metrica']}")
        st.markdown("**Premissas de limpeza aplicadas:**")
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


def grafico_subsidio_medio_faixa() -> None:
    nome = "subsidio_medio_faixa"
    meta = carregar_meta(nome)
    df = carregar_tabela(nome)

    st.subheader(meta["titulo"])
    render_ficha_proveniencia(meta)

    ordem_faixa = [
        "Faixa 1 (FAR/OGU)",
        "Faixa 1 (contratos FGTS)",
        "Faixa 2",
        "Faixa 3",
        "Faixa 4 / Classe Média",
    ]
    df = df.copy()
    df["faixa"] = pd.Categorical(df["faixa"], categories=ordem_faixa, ordered=True)
    df = df.sort_values("faixa")

    chart = (
        alt.Chart(df)
        .mark_bar(color=COR_FGTS)
        .encode(
            x=alt.X("faixa:N", title=None, sort=ordem_faixa, axis=alt.Axis(labelAngle=-20)),
            y=alt.Y("subsidio_medio_por_unidade:Q", title="R$ por unidade (valores correntes)"),
            tooltip=[
                alt.Tooltip("faixa:N", title="Faixa"),
                alt.Tooltip("subsidio_medio_por_unidade:Q", title="Subsídio médio (R$)", format=",.0f"),
                alt.Tooltip("qtd_contratos:Q", title="Nº de contratos/unidades", format=",.0f"),
            ],
        )
        .properties(height=380)
        .configure_axis(gridColor="#e1e0d9", domainColor="#c3c2b7")
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(chart, use_container_width=True)
    st.caption(
        "As duas barras de 'Faixa 1' usam definições diferentes de subsídio — ver "
        "premissas acima. Não devem ser somadas."
    )

    with st.expander("Ver tabela tidy"):
        tabela = df.set_index("faixa")[["subsidio_medio_por_unidade", "qtd_contratos"]]
        tabela.columns = ["Subsídio médio (R$)", "Nº contratos/unidades"]
        st.dataframe(tabela.round(0), use_container_width=True)


# Registro de renderers de gráfico por id — só precisa crescer conforme
# gráficos 2, 4, 5, 6 forem processados.
RENDERERS = {
    "financiamento_por_fonte_ano": grafico_financiamento_fonte_ano,
    "subsidio_medio_faixa": grafico_subsidio_medio_faixa,
}


def render_aba(aba: dict) -> None:
    st.markdown(f"**Organização responsável:** {aba['organizacao']}")
    st.caption(aba["organizacao_descricao"])
    if aba["portal"]:
        st.markdown(f"**Catálogo:** [{aba['portal']}]({aba['portal']})")
    st.divider()

    for grafico_id in aba["graficos"]:
        RENDERERS[grafico_id]()
        st.divider()

    if aba["pendente"]:
        with st.container(border=True):
            st.markdown("🚧 **Em construção — gráficos planejados para esta base:**")
            for item in aba["pendente"]:
                st.markdown(f"- {item}")


def main():
    st.title("Custo do déficit habitacional: MCMV e a sustentabilidade do FGTS")
    st.caption("Dissertação — Mestrado Profissional em Economia e Finanças, FGV EPGE")

    with st.sidebar:
        st.markdown("### 📂 Bases de dados")
        labels = [aba["label"] for aba in ABAS]
        status = [" ✅" if aba["graficos"] else " 🚧" for aba in ABAS]
        escolha = st.radio(
            "Escolha uma base para explorar",
            options=range(len(ABAS)),
            format_func=lambda i: labels[i] + status[i],
            label_visibility="collapsed",
        )

    render_aba(ABAS[escolha])


if __name__ == "__main__":
    main()
