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
        "graficos": ["arrecadacao_saques_fgts", "orcamento_fgts_rubrica"],
        "pendente": [],
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


def grafico_arrecadacao_saques() -> None:
    nome = "arrecadacao_saques_fgts"
    meta = carregar_meta(nome)
    df = carregar_tabela(nome)

    st.subheader(meta["titulo"])
    render_ficha_proveniencia(meta)

    df = df.copy()
    df["arrecadacao_bi"] = df["arrecadacao_rs_milhares"] / 1e6
    df["saques_bi"] = df["saques_rs_milhares"] / 1e6
    long = df.melt(
        id_vars="ano",
        value_vars=["arrecadacao_bi", "saques_bi"],
        var_name="serie",
        value_name="valor_bi",
    )
    long["serie"] = long["serie"].map({"arrecadacao_bi": "Arrecadação", "saques_bi": "Saques"})
    ordem_serie = ["Arrecadação", "Saques"]
    escala_cor = alt.Scale(domain=ordem_serie, range=[COR_FGTS, COR_OGU])

    chart = (
        alt.Chart(long)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("ano:O", title=None),
            y=alt.Y("valor_bi:Q", title="R$ bilhões (valores correntes)"),
            color=alt.Color("serie:N", scale=escala_cor, sort=ordem_serie, title=None),
            tooltip=[
                alt.Tooltip("ano:O", title="Ano"),
                alt.Tooltip("serie:N", title="Série"),
                alt.Tooltip("valor_bi:Q", title="R$ bilhões", format=",.1f"),
            ],
        )
        .properties(height=380)
        .configure_axis(gridColor="#e1e0d9", domainColor="#c3c2b7")
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption(
        "2020 não é comparável aos demais anos: exclui a incorporação extraordinária "
        "do PIS/PASEP (MP 946/2020) — ver premissas acima."
    )

    with st.expander("Ver tabela tidy"):
        tabela = df.set_index("ano")[["arrecadacao_rs_milhares", "saques_rs_milhares", "arrecadacao_liquida_rs_milhares"]]
        tabela.columns = ["Arrecadação (R$ mil)", "Saques (R$ mil)", "Arrecadação líquida (R$ mil)"]
        st.dataframe(tabela, use_container_width=True)

    nome_mod = "saques_por_modalidade_fgts"
    df_mod = carregar_tabela(nome_mod)
    st.markdown("**Bônus — saques por modalidade (% do total), 2020-2023**")
    st.caption(
        "Só disponível para esses 4 anos nos PDFs consultados. Inclui a fatia de "
        "\"Aposentadoria\" — um dos dois riscos estruturais do FGTS discutidos na dissertação."
    )
    ordem_mod = [
        "Demissão sem Justa Causa", "Habitação", "Aposentadoria",
        "Saque-aniversário", "Saque extraordinário", "Outras modalidades",
    ]
    cores_mod = [COR_FGTS, COR_OGU, COR_FUNDO_SOCIAL, "#eda100", "#e87ba4", "#008300"]
    chart_mod = (
        alt.Chart(df_mod)
        .mark_bar()
        .encode(
            x=alt.X("ano:O", title=None),
            y=alt.Y("percentual:Q", title="% dos saques", stack="zero"),
            color=alt.Color("modalidade:N", scale=alt.Scale(domain=ordem_mod, range=cores_mod), sort=ordem_mod, title="Modalidade"),
            order=alt.Order("modalidade:N", sort="ascending"),
            tooltip=[
                alt.Tooltip("ano:O", title="Ano"),
                alt.Tooltip("modalidade:N", title="Modalidade"),
                alt.Tooltip("percentual:Q", title="%", format=".1f"),
            ],
        )
        .properties(height=340)
        .configure_axis(gridColor="#e1e0d9", domainColor="#c3c2b7")
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart_mod, use_container_width=True)


def grafico_orcamento_fgts_rubrica() -> None:
    nome = "orcamento_fgts_rubrica"
    meta = carregar_meta(nome)
    df = carregar_tabela(nome)

    st.subheader(meta["titulo"])
    render_ficha_proveniencia(meta)

    df = df.copy()
    df["valor_bi"] = df["valor_rs_milhares"] / 1e6

    ordem_rubrica = [
        "Despesas de depósitos vinculados",
        "Descontos concedidos",
        "Taxa de administração",
        "Outras despesas operacionais e administrativas",
        "Despesas administrativas",
    ]
    cores_rubrica = [COR_FGTS, COR_OGU, COR_FUNDO_SOCIAL, "#eda100", "#e87ba4"]

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("ano:O", title=None),
            y=alt.Y("valor_bi:Q", title="R$ bilhões (valores correntes)", stack="zero"),
            color=alt.Color(
                "rubrica:N",
                scale=alt.Scale(domain=ordem_rubrica, range=cores_rubrica),
                sort=ordem_rubrica,
                title="Rubrica",
            ),
            order=alt.Order("rubrica:N", sort="ascending"),
            tooltip=[
                alt.Tooltip("ano:O", title="Ano"),
                alt.Tooltip("rubrica:N", title="Rubrica"),
                alt.Tooltip("valor_bi:Q", title="R$ bilhões", format=",.1f"),
            ],
        )
        .properties(height=420)
        .configure_axis(gridColor="#e1e0d9", domainColor="#c3c2b7")
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption(
        "\"Descontos concedidos\" = subsídio explícito de taxa de juros. Composição "
        "REALIZADA, não o orçamento aprovado pelo CCFGTS — ver premissas acima."
    )

    with st.expander("Ver tabela tidy"):
        tabela_wide = df.pivot(index="ano", columns="rubrica", values="valor_bi")[ordem_rubrica]
        st.dataframe(tabela_wide.round(1), use_container_width=True)


# Registro de renderers de gráfico por id — só precisa crescer conforme
# gráficos 4 e 5 forem processados.
RENDERERS = {
    "financiamento_por_fonte_ano": grafico_financiamento_fonte_ano,
    "subsidio_medio_faixa": grafico_subsidio_medio_faixa,
    "arrecadacao_saques_fgts": grafico_arrecadacao_saques,
    "orcamento_fgts_rubrica": grafico_orcamento_fgts_rubrica,
}


# Etapas do objetivo geral da dissertação (Introdução, linha do "objetivo geral"),
# mapeadas ao que já está pronto no dashboard.
ETAPAS = [
    {
        "titulo": "Caracterizar a evolução histórica das fontes de recursos do MCMV",
        "grafico": "Gráfico 1 — Financiamento por fonte e ano",
        "pronto": True,
    },
    {
        "titulo": "Separar financiamento, subsídios explícitos e subsídios implícitos",
        "grafico": "Base conceitual do Gráfico 3",
        "pronto": True,
    },
    {
        "titulo": "Estimar o subsídio médio por unidade e por faixa de renda",
        "grafico": "Gráfico 3 — Subsídio médio por faixa",
        "pronto": True,
    },
    {
        "titulo": "Reconstruir a evolução recente das entradas, saídas e aplicações do FGTS",
        "grafico": "Gráfico 2 (despesas por rubrica) e Gráfico 6 (arrecadação x saques)",
        "pronto": True,
    },
    {
        "titulo": "Simular a trajetória do Fundo sob hipóteses de formalização do mercado de trabalho e de saques",
        "grafico": "Gráfico 4 (PNAD/Caged) + simulação — pendente",
        "pronto": False,
    },
    {
        "titulo": "Estimar a ordem de grandeza do custo de enfrentar o estoque atual do déficit habitacional",
        "grafico": "Gráfico 5 (FJP) — pendente",
        "pronto": False,
    },
]


def render_organograma() -> None:
    cor_pronto = "#1baf7a"
    cor_parcial = "#eda100"
    cor_pendente = "#c3c2b7"

    boxes_html = []
    for i, etapa in enumerate(ETAPAS, start=1):
        if etapa["pronto"] is True:
            cor, selo = cor_pronto, "✅ pronto"
        elif etapa["pronto"] == "parcial":
            cor, selo = cor_parcial, "🟡 parcial"
        else:
            cor, selo = cor_pendente, "🚧 pendente"

        boxes_html.append(
            f'<div style="border:2px solid {cor}; border-radius:10px; padding:14px 18px; '
            f'background:rgba(0,0,0,0.015); max-width:640px; margin:0 auto;">'
            f'<div style="font-size:0.78rem; color:#898781; font-weight:600;">ETAPA {i}</div>'
            f'<div style="font-size:0.95rem; font-weight:600; margin:2px 0 4px 0;">{etapa["titulo"]}</div>'
            f'<div style="font-size:0.85rem; color:#52514e;">{etapa["grafico"]}</div>'
            f'<div style="font-size:0.78rem; color:{cor}; font-weight:700; margin-top:4px;">{selo}</div>'
            f'</div>'
        )
        if i < len(ETAPAS):
            boxes_html.append(
                '<div style="text-align:center; font-size:1.4rem; color:#898781; '
                'line-height:1.2; margin: 2px 0;">↓</div>'
            )

    st.markdown("\n".join(boxes_html), unsafe_allow_html=True)


def render_capa() -> None:
    st.title("Minha Casa Minha Vida, FGTS e Déficit Habitacional")
    st.markdown(
        "##### Uma análise da sustentabilidade financeira do modelo brasileiro "
        "de financiamento habitacional"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Autor:** Arthur Messer")
        st.markdown("**Orientador:** Fernando de Holanda Barbosa Filho")
    with col2:
        st.markdown("**Instituição:** FGV EPGE — Mestrado Profissional em Economia e Finanças")
        st.markdown("**Área de concentração:** Finanças Públicas, Política Habitacional e Sustentabilidade Fiscal")

    st.divider()

    st.markdown("#### Objetivo geral")
    st.write(
        "Avaliar a sustentabilidade financeira do MCMV a partir da estrutura de "
        "financiamento do programa, com ênfase no FGTS, e entender como o programa "
        "reduz o déficit habitacional."
    )

    with st.expander("Ver resumo completo da dissertação"):
        st.write(
            "Esta dissertação avalia a sustentabilidade financeira do Programa "
            "Minha Casa, Minha Vida, principal instrumento federal de provisão e "
            "financiamento habitacional do Brasil, com ênfase no papel do Fundo de "
            "Garantia do Tempo de Serviço como fonte de recursos. O trabalho parte "
            "da distinção entre o volume de crédito aplicado no financiamento "
            "habitacional e o custo econômico efetivo do programa, separando "
            "financiamento, subsídios explícitos e subsídios implícitos decorrentes "
            "de taxas de juros inferiores às praticadas pelo mercado. A partir de "
            "bases administrativas e contábeis oficiais, estima-se o subsídio médio "
            "por unidade e por faixa de renda e reconstrói-se a evolução recente das "
            "entradas, saídas e aplicações do Fundo. Em seguida, projeta-se a "
            "trajetória financeira do Fundo sob diferentes hipóteses de formalização "
            "do mercado de trabalho e de saques, e dimensiona-se a ordem de "
            "grandeza do custo de enfrentar o estoque atual do déficit habitacional. "
            "A hipótese de que a disponibilidade de recursos do Fundo constitui a "
            "principal restrição à expansão do modelo é tratada como questão "
            "empírica, e não como resultado previamente estabelecido."
        )

    st.divider()

    st.markdown("#### Abordagem — do objetivo geral aos gráficos")
    st.caption(
        "Cada etapa abaixo corresponde a uma frase do objetivo geral da introdução, "
        "ligada ao(s) gráfico(s) deste dashboard que a implementam."
    )
    render_organograma()

    st.divider()
    st.caption(
        "Use o menu à esquerda para explorar cada base de dados. Cada gráfico traz "
        "sua própria ficha de proveniência (fonte, link, premissas) antes da figura."
    )


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
    with st.sidebar:
        st.markdown("### 🧭 Navegação")
        labels = ["📖 Capa"] + [aba["label"] for aba in ABAS]
        status = [""] + [" ✅" if aba["graficos"] else " 🚧" for aba in ABAS]
        escolha = st.radio(
            "Navegação",
            options=range(len(labels)),
            format_func=lambda i: labels[i] + status[i],
            label_visibility="collapsed",
        )

    if escolha == 0:
        render_capa()
    else:
        render_aba(ABAS[escolha - 1])


if __name__ == "__main__":
    main()
