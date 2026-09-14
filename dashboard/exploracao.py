"""Perguntas exploratórias com as bases existentes; sem chamadas de rede no app."""
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
import plotly.express as px
from ui import plot, table
from periods import period

DATA = Path(__file__).resolve().parents[1] / "data/processed"
BLUE, ORANGE, GREEN = "#1f77b4", "#ff7f0e", "#2ca02c"
COLORS = [BLUE, ORANGE, GREEN, "#d62728", "#8c6bb1", "#64748b"]


def color_scale(df, field):
    known = {"FGTS": BLUE, "OGU": ORANGE, "Empreendimentos subsidiados (proxy OGU)": ORANGE,
             "Fundo Social": GREEN, "Faixa 1*": BLUE, "Faixa 2*": ORANGE, "Faixa 3*": GREEN,
             "Faixa 4*": "#d62728", "Sem classificação": "#64748b"}
    domain = sorted(df[field.split(":")[0]].dropna().unique().tolist())
    return alt.Scale(domain=domain, range=[known.get(v, COLORS[i % len(COLORS)]) for i,v in enumerate(domain)])


def read(name):
    return pd.read_csv(DATA / f"{name}.csv")


def show(title, question, df, chart, sources, method, key, interpretation):
    st.subheader(title)
    st.write(question)
    if hasattr(chart, "update_layout"):
        plot(chart, key)
    else:
        st.altair_chart(chart.configure_view(strokeWidth=0).configure_axis(gridColor="#e1e0d9",labelFontSize=16,titleFontSize=17)
            .configure_legend(orient="bottom", labelLimit=500, columns=2,labelFontSize=16), width="stretch")
    st.caption(interpretation)
    with st.expander("Como ler e calcular este gráfico"):
        st.write(method)
    table(df, key)



def lines(df, x, y, title, color=None, pct=False):
    xf, yf = x.split(":")[0], y.split(":")[0]
    cf = color.split(":")[0] if color else None
    fig = px.line(df, x=xf, y=yf, color=cf, markers=True,
        labels={xf:"Período", yf:title}, color_discrete_sequence=COLORS)
    if pct: fig.update_yaxes(tickformat=".0%")
    return fig


def bars(df, x, y, title, color=None, pct=False, horizontal=False):
    enc = dict(x=alt.X(x, title=None, axis=alt.Axis(labelAngle=-25, labelLimit=250)),
               y=alt.Y(y, title=title, axis=alt.Axis(format=".0%") if pct else alt.Axis()),
               tooltip=[alt.Tooltip(x), alt.Tooltip(y, title=title, format=".1%" if pct else ",.2f")])
    if color:
        enc["color"] = alt.Color(color, title=None, scale=color_scale(df, color))
        enc["tooltip"].append(alt.Tooltip(color))
    if horizontal:
        enc["y"], enc["x"] = alt.Y(x, title=None, axis=alt.Axis(labelLimit=300)), alt.X(y, title=title)
    return alt.Chart(df).mark_bar(color=BLUE).encode(**enc).properties(height=430)


def render_cidades():
    st.header("Explorar fontes, escala e subsídios")
    f = period(read("financiamento_por_fonte_ano"), "fontes", partial=True)
    f["participacao"] = f.valor_total_financiado / f.groupby("ano").valor_total_financiado.transform("sum")
    f["fonte"] = f.fonte.replace({"OGU": "Empreendimentos subsidiados (proxy OGU)"})
    show("Quanto cada fonte representa no volume registrado?",
         "A dependência do FGTS muda quando olhamos participações, em vez de valores absolutos?", f,
         bars(f, "ano:O", "participacao:Q", "Participação no total registrado", "fonte:N", pct=True),
         ["financiamento_por_fonte_ano"], "Valor de cada fonte / soma dos valores disponíveis no ano. Fontes ausentes não são imputadas.",
         "composicao_fontes", "O denominador combina crédito e valor contratado de empreendimentos; não é composição do custo fiscal. Ausência de linha não comprova gasto zero. Valores de 2026 têm cortes distintos entre bases.")

    c = period(read("exploracao_contratos"), "contratos", partial=True)
    source = st.multiselect("Fonte do crédito", ["FGTS", "Fundo Social"], default=["FGTS", "Fundo Social"], key="credito_fontes")
    c = c[c.fonte.isin(source)]
    if c.empty:
        st.info("Selecione uma fonte com contratos no período para explorar o perfil.")
        return
    c["faixa"] = c.faixa_codigo.astype(str).map({"1": "Faixa 1*", "2": "Faixa 2*", "3": "Faixa 3*", "4": "Faixa 4*"}).fillna("Sem classificação")
    st.info("* Faixas inferidas dos códigos da base, ainda a validar no dicionário. Alterações dos tetos ao longo do tempo limitam comparações. Universo: operações financiadas, incluindo fonte FGTS/FS selecionada; sem FAR.")
    a = c.groupby(["ano", "faixa"], as_index=False).sum(numeric_only=True)
    a["participacao"] = a.contratos / a.groupby("ano").contratos.transform("sum")
    show("Como muda o perfil das operações financiadas?", "Quais faixas ganham participação no número de contratos?", a,
         bars(a, "ano:O", "participacao:Q", "Participação nos contratos", "faixa:N", pct=True), ["exploracao_contratos"],
         "Contagem da faixa / contagem total do ano, incluindo Sem classificação.", "perfil_contratos",
         "Mudança de composição não prova migração para a classe média: a classificação e as regras do programa mudam.")
    a["contratos_mil"] = a.contratos / 1000
    show("A mudança de participação vem com expansão de escala?", "Uma faixa pode perder participação e ainda registrar mais contratos.", a,
         lines(a, "ano:O", "contratos_mil:Q", "Mil contratos", "faixa:N"), ["exploracao_contratos"],
         "Número de operações / 1.000.", "escala_contratos", "Contratos não equivalem automaticamente a unidades entregues ou a déficit eliminado.")
    a["subsidio_medio"] = a.subsidio_total / a.contratos_subsidio_observado.replace(0, float("nan"))
    a["cobertura"] = a.contratos_subsidio_observado / a.contratos
    show("Como evolui o subsídio registrado por contrato?", "O apoio médio muda dentro de cada faixa ao longo do tempo?", a,
         lines(a, "ano:O", "subsidio_medio:Q", "R$ por contrato (correntes)", "faixa:N"), ["exploracao_contratos"],
         "Soma das quatro rubricas / contratos com todas as rubricas observadas. Cobertura disponível na tabela.", "subsidio_ano_faixa",
         "Média ponderada das operações observadas. Variações nominais incorporam inflação e mudanças de composição; não medem subsídio implícito.")
    a["financiamento_medio"] = a.financiamento / a.financiamento_observado.replace(0, float("nan"))
    show("Qual é o valor médio financiado por operação?", "A escala em reais cresce por mais contratos, por maior valor por contrato ou por ambos?", a,
         lines(a, "ano:O", "financiamento_medio:Q", "R$ por contrato (correntes)", "faixa:N"), ["exploracao_contratos"],
         "Soma financiada / operações com financiamento observado.", "ticket_financiado",
         "Valor financiado não é preço do imóvel nem custo público. Sem correção inflacionária.")
    a["incidencia_subsidio"] = a.contratos_com_subsidio / a.contratos_subsidio_observado.replace(0, float("nan"))
    show("Quantos contratos têm subsídio registrado positivo?", "Uma média baixa resulta de poucos beneficiados ou de pequenos valores por beneficiado?", a,
         lines(a, "ano:O", "incidencia_subsidio:Q", "Parcela dos contratos observados", "faixa:N", pct=True), ["exploracao_contratos"],
         "Operações com soma das rubricas > 0 / operações com rubricas completas.", "incidencia_subsidio",
         "Ausente não é zero. Não receber subsídio registrado não significa ausência de benefício de taxa.")
    t = a.groupby("faixa", as_index=False).sum(numeric_only=True)
    t["Contratos"] = t.contratos / t.contratos.sum()
    t["Subsídio registrado"] = t.subsidio_total / t.subsidio_total.sum() if t.subsidio_total.sum() else float("nan")
    t = t[["faixa", "Contratos", "Subsídio registrado"]].melt(id_vars="faixa", value_vars=["Contratos", "Subsídio registrado"], var_name="medida", value_name="participacao")
    ch = bars(t, "faixa:N", "participacao:Q", "Participação no período selecionado", "medida:N", pct=True).encode(xOffset="medida:N")
    show("Quem concentra contratos e subsídios?", "A distribuição do apoio acompanha a distribuição das operações?", t, ch,
         ["exploracao_contratos"], "Participação da faixa nas contagens e no subsídio observado; cada denominador soma 100% quando positivo.",
         "concentracao_subsidios", "O universo inclui apenas financiamento. Lacunas nas rubricas de subsídio podem afetar a comparação.")
    s = c.groupby("ano", as_index=False)[["subsidio_fgts", "subsidio_ogu"]].sum().melt("ano", var_name="fonte_subsidio", value_name="valor")
    s["fonte_subsidio"] = s.fonte_subsidio.map({"subsidio_fgts": "FGTS", "subsidio_ogu": "OGU"})
    s["valor_bi"] = s.valor / 1e9
    show("De onde vem o subsídio dos contratos financiados?", "Separando as rubricas, qual é o peso do FGTS e do OGU no apoio registrado?", s,
         bars(s, "ano:O", "valor_bi:Q", "R$ bilhões (correntes)", "fonte_subsidio:N"), ["exploracao_contratos"],
         "FGTS = desconto FGTS + equilíbrio FGTS; OGU = desconto OGU + equilíbrio OGU. Somente registros completos.",
         "subsidios_por_fonte", "Fonte do subsídio difere da fonte do crédito. Não inclui FAR, execução orçamentária ou valor presente de benefício de taxa.")


def stress_grid(arrecadacao, saques):
    rows = [{"queda_arrecadacao": q/100, "alta_saques": s/100,
             "saldo_bi": (arrecadacao*(1-q/100)-saques*(1+s/100))/1e6}
            for q in range(0, 31, 5) for s in range(0, 31, 5)]
    return pd.DataFrame(rows)


def render_fgts():
    st.header("Explorar pressão sobre os recursos do FGTS")
    st.info("A base de despesas é uma DRE. Ela não responde quanto das aplicações vai para habitação, saneamento ou infraestrutura; o orçamento inicial de 2026 está no bloco acima; a série de execução setorial permanece pendente.")
    a = period(read("arrecadacao_saques_fgts"), "fgts")
    if a.empty:return
    a["saldo_bi"] = (a.arrecadacao_rs_milhares-a.saques_rs_milhares)/1e6
    a["saques_arrecadacao"] = a.saques_rs_milhares/a.arrecadacao_rs_milhares
    show("Quanto sobra entre arrecadação e saques?", "Em quais anos a contribuição líquida dos trabalhadores foi menor?", a,
         bars(a, "ano:O", "saldo_bi:Q", "R$ bilhões (correntes)").encode(color=alt.condition(alt.datum.saldo_bi < 0, alt.value(ORANGE), alt.value(BLUE))),
         ["arrecadacao_saques_fgts"], "Arrecadação recebida menos saques pagos, dividido por 1 milhão (origem em R$ mil).", "saldo_arrecadacao",
         "Este saldo não é caixa livre, lucro ou medida de solvência: faltam os demais fluxos. 2020 exclui a transferência extraordinária do PIS/PASEP conforme a base original.")
    ch = lines(a, "ano:O", "saques_arrecadacao:Q", "Saques / arrecadação", pct=True)
    ch.add_hline(y=1, line_dash="dash", line_color=ORANGE)
    show("Quanto da arrecadação é absorvido pelos saques?", "A pressão aumenta mesmo quando a arrecadação cresce?", a, ch,
         ["arrecadacao_saques_fgts"], "Saques / arrecadação. Linha de referência = 100%.", "pressao_saques",
         "Acima de 100%, saques superam arrecadação; isso isoladamente não demonstra insolvência.")
    r = read("orcamento_fgts_rubrica")
    r = r[r.ano.isin(a.ano)].copy()
    r["participacao"] = r.valor_rs_milhares / r.groupby("ano").valor_rs_milhares.transform("sum")
    show("Como se distribuem as despesas contábeis?", "O peso dos descontos cresce em relação às outras rubricas da DRE?", r,
         bars(r, "ano:O", "participacao:Q", "Participação nas cinco rubricas", "rubrica:N", pct=True), ["orcamento_fgts_rubrica"],
         "Valor da rubrica / soma das cinco rubricas transcritas no ano.", "composicao_despesas",
         "Despesas contábeis não são aplicações de crédito por setor nem orçamento aprovado. A participação dos descontos não é a participação do MCMV nas aplicações do Fundo.")
    r["valor_bi"] = r.valor_rs_milhares / 1e6
    show("Descontos e remuneração das contas evoluem juntos?", "Quais componentes explicam a variação das despesas?", r,
         lines(r, "ano:O", "valor_bi:Q", "R$ bilhões (correntes)", "rubrica:N"), ["orcamento_fgts_rubrica"],
         "Valores das rubricas / 1 milhão, pois a origem está em R$ mil.", "trajetoria_despesas",
         "A rubrica de descontos não é uma estimativa de todo o subsídio implícito de juros. Crescimento nominal não mede crescimento real.")
    m = read("saques_por_modalidade_fgts")
    m = m[m.ano.isin(a.ano)]
    if m.empty:
        st.info("A abertura por modalidade cobre 2020–2023. Amplie o período para consultar esse gráfico.")
    if not m.empty:
        m = m.copy()
        m["participacao"] = m.percentual/100
        show("Quais modalidades ganham peso nos saques?", "Como evoluem aposentadoria, saque-aniversário e as demais modalidades?", m,
             lines(m, "ano:O", "participacao:Q", "Participação nos saques", "modalidade:N", pct=True), ["arrecadacao_saques_fgts"],
             "Percentuais originais / 100; não extrapola além de 2020–2023 nem preenche modalidades ausentes.", "modalidades_trajetoria",
             "Participação pode crescer sem aumento do valor absoluto. Não se multiplica pela DFC sem conciliar os universos das tabelas.")
    st.markdown("#### Sensibilidade estática de arrecadação e saques")
    yr = st.selectbox("Ano de referência do exercício", sorted(a.ano.tolist()), index=len(a)-1, key="stress_ano")
    b = a[a.ano == yr].iloc[0]
    grid = stress_grid(b.arrecadacao_rs_milhares, b.saques_rs_milhares)
    grid["queda_rotulo"] = grid.queda_arrecadacao.map(lambda x: f"{x:.0%}")
    grid["alta_rotulo"] = grid.alta_saques.map(lambda x: f"{x:.0%}")
    labels = [f"{x}%" for x in range(0,31,5)]
    heat = alt.Chart(grid).mark_rect().encode(
        x=alt.X("queda_rotulo:O", sort=labels, title="Queda da arrecadação"),
        y=alt.Y("alta_rotulo:O", sort=labels, title="Alta dos saques"),
        color=alt.Color("saldo_bi:Q", title="Saldo (R$ bi)", scale=alt.Scale(scheme="redblue", domainMid=0)),
        tooltip=[alt.Tooltip("queda_arrecadacao:Q", format=".0%"), alt.Tooltip("alta_saques:Q", format=".0%"), alt.Tooltip("saldo_bi:Q", format=".2f")]).properties(height=330)
    show("Quando arrecadação menos saques fica negativo?", f"Aplicação de choques hipotéticos aos valores observados em {yr}.", grid, heat,
         ["arrecadacao_saques_fgts"], "Saldo = A × (1 − queda) − S × (1 + alta). Choques em %, valores de referência mantidos constantes.",
         "sensibilidade_fluxo", "Exercício parcial de um ano, sem probabilidades. Não projeta saldo do Fundo, amortizações, rendimentos, remuneração ou novos financiamentos; não é teste completo de sustentabilidade.")


def render_emprego():
    st.header("Explorar a base potencial de contribuição")
    d = period(read("formalizacao_pnad"), "pnad")
    if d.empty:return
    d["periodo"] = d.ano.astype(str)+"T"+d.trimestre.astype(str)
    d["outros_ocupados"] = d.total_ocupados-d.com_carteira_fgts
    t = d.melt(id_vars="periodo", value_vars=["com_carteira_fgts", "outros_ocupados"], var_name="grupo", value_name="mil_pessoas")
    t["grupo"] = t.grupo.map({"com_carteira_fgts":"Com carteira (proxy FGTS)", "outros_ocupados":"Demais ocupados"})
    t["milhoes"] = t.mil_pessoas/1000
    show("O número de ocupados com carteira acompanha a ocupação?", "É possível crescer em pessoas e perder participação no emprego total.", t,
         lines(t, "periodo:O", "milhoes:Q", "Milhões de pessoas", "grupo:N"), ["formalizacao_pnad"],
         "Pessoas em milhares na tabela SIDRA / 1.000. Demais = total − categorias com carteira.", "ocupacao_niveis",
         "Demais ocupados não significa apenas informais ou pessoas jurídicas. A PNAD conta pessoas; não identifica depósitos efetivos nem todos os vínculos.")
    idx = d[["periodo", "total_ocupados", "com_carteira_fgts"]].copy()
    base = idx.iloc[0]
    for col in ["total_ocupados", "com_carteira_fgts"]:
        idx[col] = idx[col]/base[col]*100
    idx = idx.melt(id_vars="periodo", var_name="serie", value_name="indice")
    idx["serie"] = idx.serie.map({"total_ocupados":"Total de ocupados", "com_carteira_fgts":"Com carteira (proxy FGTS)"})
    show("Qual grupo cresce mais desde o início do período?", f"Compare trajetórias com {base.periodo} = 100.", idx,
         lines(idx, "periodo:O", "indice:Q", "Índice (início = 100)", "serie:N"), ["formalizacao_pnad"],
         "Nível em cada trimestre / nível no primeiro trimestre selecionado × 100.", "ocupacao_indice",
         "O índice compara crescimento proporcional, não tamanho. A escolha da base altera a leitura.")
    full = read("formalizacao_pnad").sort_values(["ano", "trimestre"])
    full["variacao_pp"] = (full.taxa_formalizacao_fgts-full.taxa_formalizacao_fgts.shift(4))*100
    full["periodo"] = full.ano.astype(str)+"T"+full.trimestre.astype(str)
    yoy = full[full.ano.isin(d.ano)].dropna(subset=["variacao_pp"])
    if not yoy.empty:
        show("A participação com carteira aumenta frente ao mesmo trimestre anterior?", "Comparar o mesmo trimestre reduz a influência da sazonalidade.", yoy,
             bars(yoy, "periodo:O", "variacao_pp:Q", "Variação em pontos percentuais").encode(color=alt.condition(alt.datum.variacao_pp<0,alt.value(ORANGE),alt.value(BLUE))),
             ["formalizacao_pnad"], "100 × (taxa no trimestre − taxa quatro trimestres antes). Referência usa a série completa, mesmo fora do filtro.",
             "formalizacao_variacao", "Variação em pontos percentuais, não em %. Sem intervalos de confiança, não se afirma significância estatística nem causalidade de pejotização.")
    last = d.iloc[-1]
    pp = st.slider("Mudança hipotética na participação com carteira (p.p.)", -10.0, 10.0, -2.0, 0.5, key="choque_formalizacao")
    wage = st.slider("Mudança hipotética no salário médio nominal (%)", -10, 20, 0, key="choque_salario")
    base_rate = last.taxa_formalizacao_fgts
    scenario_rate = base_rate+pp/100
    scenario = pd.DataFrame({"cenario":["Referência", "Hipótese selecionada"],
                             "indice_contribuicao":[100, 100*(scenario_rate/base_rate)*(1+wage/100)]})
    show("Como formalização e salário alterariam a contribuição potencial?", f"Sensibilidade relativa a {last.periodo}, mantendo a ocupação total fixa.", scenario,
         bars(scenario, "cenario:N", "indice_contribuicao:Q", "Índice de contribuição potencial"), ["formalizacao_pnad"],
         f"Índice = 100 × (participação simulada / {base_rate:.6f}) × (1 + variação salarial). Hipóteses selecionadas: {pp:+.1f} p.p. e {wage:+d}% de salário; alíquota e recolhimento constantes.",
         "sensibilidade_formalizacao", "Modelo proporcional ilustrativo, sem projeção demográfica ou salarial e sem inferir arrecadação efetiva. Pejotização é uma hipótese possível, não uma conclusão desta base.")


def render_exploracao(index):
    {0: render_cidades, 1: render_fgts, 2: render_emprego}[index]()
