"""Comparações históricas: mutuário e Fundo têm contrafactuais distintos."""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from periods import period
from ui import DATA, COLORS, plot, table


def annual_contract_rates(monthly, market, nominal=False):
    """Usa os mesmos principais/mês nos dois lados; mantém denominador de cobertura."""
    d = monthly.merge(market, on='mes', how='left', validate='many_to_one')
    d['ano'] = d.mes.str[:4].astype(int)
    matched = d.mercado_pct_aa.notna() & d.principal_taxa_valida.gt(0)
    d['principal_comparado'] = d.principal_taxa_valida.where(matched, 0)
    numerator = 'soma_taxa_equivalente_principal' if nominal else 'soma_taxa_principal'
    d['numerador_contrato'] = d[numerator].where(matched, 0)
    d['numerador_mercado'] = (d.mercado_pct_aa*d.principal_comparado).fillna(0)
    a = d.groupby('ano', as_index=False)[['contratos','contratos_taxa_valida','financiamento_total',
        'principal_taxa_valida','principal_comparado','numerador_contrato','numerador_mercado']].sum()
    denominator = a.principal_comparado.replace(0, np.nan)
    a['contrato_pct_aa'] = a.numerador_contrato/denominator
    a['mercado_pct_aa'] = a.numerador_mercado/denominator
    a['diferencial_pp'] = a.mercado_pct_aa-a.contrato_pct_aa
    a['cobertura_principal_pct'] = 100*a.principal_comparado/a.financiamento_total.replace(0,np.nan)
    a['cobertura_taxa_contratos_pct'] = 100*a.contratos_taxa_valida/a.contratos
    return a


def opportunity_estimate(data, adjustment_pp=0):
    d = data.copy()
    d['ajuste_cenario_pp'] = adjustment_pp
    d['referencia_pct_ano'] = d.selic_pct_ano+adjustment_pp
    d['receita_alternativa_rs_milhares'] = d.saldo_medio_rs_milhares*d.referencia_pct_ano/100
    d['diferencial_rs_milhares'] = d.receita_alternativa_rs_milhares-d.receita_rs_milhares
    return d


def comparison_figure(d, columns, unit, subtitle=None):
    t = d[['ano']+list(columns)].rename(columns=columns).melt('ano', var_name='Série', value_name=unit)
    fig = px.bar(t, x='ano', y=unit, color='Série', barmode='group',
                 color_discrete_sequence=COLORS, text_auto='.1f', labels={'ano':'Ano'})
    fig.update_traces(textposition='outside', cliponaxis=False,
                      hovertemplate='%{x:.0f}<br>%{y:.2f}<extra>%{fullData.name}</extra>')
    years = sorted(d.ano.unique())
    fig.update_xaxes(type='linear', tickmode='array', tickvals=years,
                     ticktext=[str(y)+('*' if y==2026 else '') for y in years],
                     range=[min(years)-.6,max(years)+.6])
    fig.update_yaxes(rangemode='tozero')
    if subtitle:
        fig.update_layout(title=dict(text=subtitle,x=.02,font=dict(size=14)))
    return fig


def render_contract_rates():
    st.header('Juros históricos dos contratos')
    st.write('Taxas iniciais dos contratos de cada ano, ponderadas pelo valor financiado. '
             'São observações históricas, distintas da tabela normativa de junho de 2026.')
    monthly = pd.read_csv(DATA/'juros_contratos_mensal.csv', dtype={'faixa_codigo':str})
    market = pd.read_csv(DATA/'juros_mercado_bcb.csv')
    c1,c2 = st.columns(2)
    selected_sources = c1.multiselect('Fonte do crédito neste comparativo', ['FGTS','Fundo Social'],
                                      default=['FGTS'], key='opportunity_sources')
    codes = c2.multiselect('Códigos de faixa neste comparativo',
                          ['1','2','3','4','Sem classificação'],
                          default=['1','2','3','4','Sem classificação'], key='opportunity_codes')
    convention = st.radio('Convenção da taxa do contrato · hipótese de comparação',
        ['Valor informado na base','Nominal anual → equivalente com capitalização mensal'],
        key='opportunity_convention', horizontal=True)
    selected = monthly[monthly.fonte.isin(selected_sources) & monthly.faixa_codigo.isin(codes)]
    if selected.empty:
        st.info('Selecione ao menos uma fonte e uma faixa com observações.')
        return
    if market.empty:
        # Sem benchmark, mostrar somente os dados observados, sem inventar um spread.
        selected = selected.copy()
        selected['ano'] = selected.mes.str[:4].astype(int)
        annual = selected.groupby('ano',as_index=False).sum(numeric_only=True)
        numerator = ('soma_taxa_equivalente_principal' if convention.startswith('Nominal') else 'soma_taxa_principal')
        annual['contrato_pct_aa'] = annual[numerator]/annual.principal_taxa_valida.replace(0,np.nan)
        annual['cobertura_principal_pct'] = 100*annual.principal_taxa_valida/annual.financiamento_total.replace(0,np.nan)
        annual['cobertura_taxa_contratos_pct'] = 100*annual.contratos_taxa_valida/annual.contratos
        d = period(annual,'opportunity_contracts',partial=True,default=(2009,2025))
        if d.empty:return
        st.subheader('Taxa inicial contratada, ano a ano')
        plot(comparison_figure(d,{'contrato_pct_aa':'MCMV · taxa contratada'},'% · leitura anual assumida'), 'opportunity_rates')
        st.caption('Taxas históricas, ponderadas pelo principal. Convenção nominal/efetiva não confirmada no dicionário SNH; '
                   'a conversão é hipótese selecionável, não alteração dos dados. Não inclui seguros, tarifas ou atualização do saldo.')
        st.info('A série de mercado BCB 20772 não respondeu à consulta de 19/10/2026. '
                'O diferencial mutuário–mercado permanece sem cálculo. A estimativa com Selic na aba FGTS está disponível.')
        d['convencao'] = convention
        d['fontes_selecionadas'] = ', '.join(selected_sources)
        d['faixas_selecionadas'] = ', '.join(codes)
        st.caption(f'Cobertura do principal: {d.cobertura_principal_pct.min():.1f}% a {d.cobertura_principal_pct.max():.1f}% por ano. '
                   'Taxas ausentes não viram zero. Códigos de faixa têm interpretação exploratória; limites de renda mudam no tempo.')
        table(d,'opportunity_rates_audit')
        return
    annual = annual_contract_rates(selected, market, nominal=convention.startswith('Nominal'))
    annual = annual[annual.principal_comparado.gt(0)]
    d = period(annual,'opportunity_contracts',partial=True,default=(2011,2025))
    if d.empty:return
    st.subheader('Taxa inicial contratada e crédito imobiliário de mercado')
    plot(comparison_figure(d, {'contrato_pct_aa':'MCMV · taxa contratada',
                             'mercado_pct_aa':'BCB · referência de mercado'}, '% a.a.'), 'opportunity_rates')
    st.caption('Contratos históricos; não utiliza a tabela normativa de 2026. BCB SGS 20772, desde março de 2011. '
               'A convenção nominal/efetiva da base SNH não está confirmada; as duas opções são hipóteses de leitura. '
               'Indexadores, risco e prazos não estão harmonizados. Não é uma comparação de CET.')
    st.subheader('Distância para a referência de mercado, ano a ano')
    plot(comparison_figure(d, {'diferencial_pp':'Referência BCB menos taxa contratada'},
                           'Pontos percentuais'), 'opportunity_spread')
    st.caption('Diferença exploratória de taxas. Não representa subsídio implícito, benefício causal '
               'ou custo do FGTS. A taxa do mutuário inclui remunerações que não pertencem integralmente ao Fundo.')
    st.write(f'Cobertura do valor financiado neste recorte: de {d.cobertura_principal_pct.min():.1f}% '
             f'a {d.cobertura_principal_pct.max():.1f}% por ano. '
             'A tabela informa também a cobertura de contratos com taxa válida.')
    st.caption('Meses sem referência do BCB e contratos sem taxa/principal válidos ficam fora da média; '
               'não são preenchidos com zero. Em 2011, janeiro e fevereiro ficam fora da comparação. '
               'Códigos de faixa seguem a classificação exploratória da base; limites de renda mudam no tempo.')
    exported = d.copy()
    exported['convencao'] = convention
    exported['fontes_selecionadas'] = ', '.join(selected_sources)
    exported['faixas_selecionadas'] = ', '.join(codes)
    table(exported,'opportunity_rates_audit')


def render_fund_opportunity():
    st.header('Subsídios e custo de oportunidade, ano a ano')
    st.write('Quanto a carteira habitacional do FGTS rendeu e quanto renderia à Selic? '
             'O exercício usa receitas contábeis e saldos da própria carteira, de 2021 a 2025.')
    st.caption('ESCOPO · Carteira habitacional total do FGTS, incluindo operações antigas, FAR e dívida subordinada. '
               'Não é uma estimativa exclusiva do MCMV. Valores correntes; regime de competência, não fluxo de caixa.')
    raw = pd.read_csv(DATA/'custo_oportunidade_fgts.csv')
    d = period(raw,'opportunity_fund',default=(2021,2025))
    if d.empty:return
    adjustment = st.slider('Ajuste da referência em relação à Selic · pontos percentuais ao ano',
                            -5.0,5.0,0.0,0.5,key='opportunity_adjustment')
    d = opportunity_estimate(d, adjustment)
    subtitle = 'Carteira habitacional total · cenário Selic '+f'({adjustment:+.1f} p.p.)'.replace('.',',')+' · valores brutos'
    st.caption('0 p.p. = Selic acumulada em cada ano. O ajuste é uma hipótese de sensibilidade, '
               'não uma estimativa observada de custos ou prêmio de risco.')
    st.subheader('Retorno da carteira habitacional e referência financeira')
    plot(comparison_figure(d, {'retorno_contabil_bruto_pct':'Carteira · retorno contábil bruto',
                             'referencia_pct_ano':'Referência · Selic ajustada'}, '% ao ano',subtitle), 'opportunity_fund_rates')
    st.caption('Retorno da carteira = juros, encargos e atualização monetária reconhecidos / saldo médio bruto. '
               'Saldo médio aproximado pela média dos saldos de abertura e encerramento. '
               'Selic anual composta pelos 12 meses, não a meta ao final do ano.')
    for field in ['receita_rs_milhares','receita_alternativa_rs_milhares','diferencial_rs_milhares',
                  'descontos_fgts_dre_rs_milhares']:
        d[field+'_bi'] = d[field]/1e6
    st.subheader('Receita da carteira e receita no cenário alternativo')
    plot(comparison_figure(d, {'receita_rs_milhares_bi':'Carteira · receita reconhecida',
              'receita_alternativa_rs_milhares_bi':'Cenário · receita alternativa'}, 'R$ bilhões',subtitle), 'opportunity_fund_income')
    st.caption('Receita alternativa = saldo médio bruto × referência anual. Comparação bruta, sem deduzir '
               'perdas, despesas, impostos ou remuneração dos cotistas. Não afirma que toda a carteira '
               'poderia ser convertida em títulos públicos nas mesmas condições de prazo, risco e alocação legal.')
    st.subheader('Descontos registrados e diferencial de retorno estimado')
    fig = comparison_figure(d, {'descontos_fgts_dre_rs_milhares_bi':'FGTS · descontos na DRE',
              'diferencial_rs_milhares_bi':'Habitação · diferencial estimado'}, 'R$ bilhões',subtitle)
    fig.add_hline(y=0,line_width=1,line_color='#65778A')
    plot(fig,'opportunity_fund_cost')
    st.caption('Descontos: despesa registrada do Fundo inteiro. Diferencial: receita alternativa menos receita '
               'da carteira habitacional. Positivo = retorno abaixo da referência; negativo = acima. '
               'São medidas de escopos distintos, apresentadas lado a lado; não somar como “custo total do MCMV”. '
               'A redução de encargos já financiada por descontos/equilíbrio exige reconciliação para evitar dupla contagem.')
    table(d,'opportunity_fund_audit')
    with st.expander('Como interpretar esta estimativa'):
        st.code('Diferencial anual = [(saldo inicial + saldo final) / 2] × referência anual − receita contábil', language=None)
        st.write('Este é um primeiro cenário histórico de custo de oportunidade bruto. Para uma estimativa líquida '
                 'e exclusiva do MCMV ainda faltam saldos e receitas por programa, trajetória mensal da carteira, '
                 'perdas e despesas atribuíveis e uma alternativa compatível com o risco e o prazo. '
                 'Um diferencial positivo não demonstra insolvência; um diferencial negativo não elimina os descontos concedidos.')
        st.write('Não há extrapolação para 2020, cujo saldo inicial desta carteira não foi apurado, '
                 'nem para 2026, sem demonstração anual nesta base. As receitas e saldos são identificados por documento '
                 'e localizador na tabela para download.')
