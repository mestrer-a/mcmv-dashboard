"""Taxas nominais da linha financiada do MCMV, edição oficial de 2026."""
import pandas as pd
import plotly.express as px
import streamlit as st

from ui import COLORS, plot, table

FONTE = (
    'https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/'
    'habitacao/programa-minha-casa-minha-vida/mcmv-fgts'
)

# Transcrição da tabela do Ministério das Cidades atualizada em 28/06/2026.
# Acima de R$ 3.500, a fonte agrupa as regiões: por isso a taxa é repetida para
# N/NE e S/SE/CO, preservando apenas a diferença entre cotista e não cotista.
TAXAS_2026 = [
    ('Faixa 1', 'Até R$ 2.160', 4.00, 4.25, 4.50, 4.75),
    ('Faixa 1', 'R$ 2.160,01–2.850', 4.25, 4.50, 4.75, 5.00),
    ('Faixa 1', 'R$ 2.850,01–3.200', 4.50, 4.75, 5.00, 5.25),
    ('Faixa 2', 'R$ 3.200,01–3.500', 4.75, 5.00, 5.25, 5.50),
    ('Faixa 2', 'R$ 3.500,01–4.000', 5.50, 5.50, 6.00, 6.00),
    ('Faixa 2', 'R$ 4.000,01–5.000', 6.50, 6.50, 7.00, 7.00),
    ('Faixa 3', 'R$ 5.000,01–9.600', 7.66, 7.66, 8.16, 8.16),
    ('Classe Média', 'R$ 9.600,01–13.000', 10.00, 10.00, 10.00, 10.00),
]
COLUNAS = [
    'Faixa', 'Renda familiar mensal', 'Cotista · N/NE',
    'Cotista · S/SE/CO', 'Não cotista · N/NE', 'Não cotista · S/SE/CO',
]
COLUNAS_TAXAS = COLUNAS[2:]
FAIXAS = ['Faixa 1', 'Faixa 2', 'Faixa 3', 'Classe Média']
REGIOES = {
    'Norte e Nordeste': ('Cotista · N/NE', 'Não cotista · N/NE'),
    'Sul, Sudeste e Centro-Oeste': ('Cotista · S/SE/CO', 'Não cotista · S/SE/CO'),
}


def tabela_taxas():
    return pd.DataFrame(TAXAS_2026, columns=COLUNAS)


def primeira_prestacao_sac(principal, meses, taxa_aa):
    """Primeira prestação no SAC simplificado, com taxa nominal mensal aa/12."""
    return principal / meses + principal * (taxa_aa / 1200.0)


def render_juros_2026():
    st.header('Condições de juros do MCMV · tabela oficial de 2026')
    st.write(
        'Além dos descontos registrados, as famílias podem acessar taxas de juros '
        'definidas pelo programa. Estes gráficos descrevem as condições oficiais; '
        '**não calculam subsídio implícito nem custo para o FGTS**.'
    )
    st.info(
        'Esta seção usa uma tabela normativa fixa, atualizada em 28/06/2026. '
        'O filtro temporal da aba se aplica às séries históricas de contratos, não a estas taxas.'
    )
    st.caption(
        'Ministério das Cidades · linha financiada · taxas nominais anuais oficiais de 2026. '
        'Não são taxas médias observadas nos contratos de 2023–2025.'
    )
    st.markdown(f'[Consultar a tabela oficial das taxas]({FONTE})')
    base = tabela_taxas()

    st.subheader('1. Taxas mínimas e máximas por faixa')
    limites = pd.DataFrame({
        'Faixa': FAIXAS,
        'Menor taxa oficial de 2026': [
            base.loc[base.Faixa.eq(f), COLUNAS_TAXAS].min().min() for f in FAIXAS
        ],
        'Maior taxa oficial de 2026': [
            base.loc[base.Faixa.eq(f), COLUNAS_TAXAS].max().max() for f in FAIXAS
        ],
    })
    formato = limites.melt(
        id_vars='Faixa', var_name='Referência', value_name='Taxa nominal (% a.a.)'
    )
    fig = px.bar(
        formato, x='Faixa', y='Taxa nominal (% a.a.)', color='Referência',
        barmode='group', category_orders={'Faixa': FAIXAS},
        color_discrete_sequence=[COLORS[0], COLORS[1]],
    )
    fig.update_traces(texttemplate='%{y:.2f}%', textposition='outside', cliponaxis=False)
    fig.update_yaxes(range=[0, 11.5])
    plot(fig, 'juros_faixas_2026')
    table(limites, 'juros_faixas_2026')
    st.caption(
        'Menor e maior taxa oficial em cada faixa, considerando renda, região e condição '
        'de cotista. Não são médias contratadas e não medem o tamanho do subsídio.'
    )

    st.subheader('2. Taxas por renda, região e condição de cotista')
    regiao = st.selectbox('Região para comparação', list(REGIOES), key='juros_regiao_2026')
    cols = REGIOES[regiao]
    detalhada = base[['Faixa', 'Renda familiar mensal', *cols]].copy()
    detalhada['Renda / faixa'] = detalhada['Faixa'] + ' · ' + detalhada['Renda familiar mensal']
    mapa = {cols[0]: 'Cotista do FGTS', cols[1]: 'Não cotista'}
    longa = detalhada.melt(
        id_vars=['Renda / faixa'], value_vars=list(cols),
        var_name='Condição', value_name='Taxa nominal (% a.a.)',
    )
    longa['Condição'] = longa['Condição'].map(mapa)
    ordem = detalhada['Renda / faixa'].tolist()
    fig = px.bar(
        longa, x='Renda / faixa', y='Taxa nominal (% a.a.)', color='Condição',
        barmode='group', category_orders={'Renda / faixa': ordem},
        color_discrete_sequence=[COLORS[0], COLORS[1]],
    )
    fig.update_traces(texttemplate='%{y:.2f}%', textposition='outside', cliponaxis=False)
    fig.update_yaxes(range=[0, 11.5])
    fig.update_xaxes(tickangle=-35)
    plot(fig, 'juros_renda_2026')
    table(detalhada.drop(columns='Renda / faixa'), 'juros_renda_2026')
    st.caption(
        'Tabela oficial de 2026. Nas linhas acima de R$ 3.500, a fonte agrupa as regiões; '
        'as taxas foram repetidas nos dois grupos regionais, sem criar uma diferença inexistente. '
        'A diferença entre cotista e não cotista não equivale automaticamente ao custo do FGTS.'
    )

    st.subheader('3. Simulação ilustrativa da primeira prestação pelo SAC')
    st.write(
        'O exercício mantém valor financiado e prazo iguais e altera somente a taxa oficial. '
        'Ele serve para comparar taxas e não representa proposta de financiamento.'
    )
    c1, c2 = st.columns(2)
    with c1:
        principal = st.slider(
            'Valor hipotético financiado (R$)', 50000, 300000, 150000, 10000,
            key='juros_principal_2026',
        )
    with c2:
        anos = st.slider(
            'Prazo hipotético (anos)', 10, 35, 30, 5, key='juros_prazo_2026'
        )
    prest = longa.copy()
    prest['Primeira prestação SAC (R$)'] = prest['Taxa nominal (% a.a.)'].map(
        lambda taxa: primeira_prestacao_sac(principal, anos * 12, taxa)
    )
    fig = px.bar(
        prest, x='Renda / faixa', y='Primeira prestação SAC (R$)', color='Condição',
        barmode='group', category_orders={'Renda / faixa': ordem},
        color_discrete_sequence=[COLORS[0], COLORS[1]],
    )
    fig.update_xaxes(tickangle=-35)
    plot(fig, 'juros_prestacao_2026')
    table(prest, 'juros_prestacao_2026')
    st.caption(
        'SAC simplificado: primeira prestação = principal / meses + principal × taxa nominal '
        'anual / 12. Não inclui TR, seguros, tarifas, atualização do saldo ou descontos. '
        'O mesmo principal é usado apenas para comparação e não pressupõe elegibilidade ou '
        'aprovação de crédito. **Não é estimativa de subsídio implícito ou de custo do FGTS.**'
    )

    with st.expander('Tabela completa e critérios de transcrição'):
        st.dataframe(base, hide_index=True, width='stretch')
        st.download_button(
            'Baixar tabela oficial transcrita (CSV)',
            base.to_csv(index=False).encode('utf-8-sig'),
            file_name='taxas_mcmv_2026.csv', mime='text/csv',
            key='juros_tabela_completa_csv',
        )
        st.write(
            'As células ministeriais agrupadas foram repetidas somente para permitir a '
            'comparação regional no gráfico. Pró-Cotista não entra neste recorte porque '
            'não constitui uma quinta faixa de renda do MCMV.'
        )
