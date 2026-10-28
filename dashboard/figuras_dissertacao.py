"""Reproduções fixas e auditáveis das 15 figuras da revisão FAR da dissertação.

Os filtros exploratórios das outras seções não alteram o recorte do documento.
"""
import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from far import far_subsidy
from juros import tabela_taxas, COLUNAS_TAXAS, FAIXAS, FONTE
from ui import DATA, COLORS, plot, table

SECTIONS = {1: 'Programa e subsídios', 2: 'FGTS', 4: 'Déficit habitacional',
            6: 'Sustentabilidade e simulações'}


def spec(title, page, period, unit, kind, bases, formula, assumptions):
    return dict(title=title, page=page, period=period, unit=unit, kind=kind,
                bases=bases.split(), formula=formula, assumptions=assumptions)


FIGURES = {
    '1': spec('Subsídio registrado por contrato financiado e por faixa, 2023–2025', 1,
        '2023–2025, anos completos', 'R$ correntes por contrato', 'Dados observados · agregação administrativa',
        'exploracao_contratos', 'Σ(desconto FGTS + equilíbrio FGTS + desconto OGU + equilíbrio OGU) / contratos com as quatro rubricas preenchidas, incluindo zeros.',
        'FGTS e Fundo Social; exclui FAR. Zero registrado não exclui benefício de juros. Não é custo econômico completo.'),
    '1A': spec('Subsídio líquido FAR: referência e sensibilidade', 1,
        'Contratações FAR 2024–2025; recebimentos hipotéticos nos meses 1–60', 'R$ mil de dezembro de 2025 por unidade', 'Cenários calculados',
        'far_anual sim_parametros', 'S = V − (1−e)(1−λ) × Σ[m=1…60] (0,10V/60)/(1+0,06)^(m/12).',
        'V = R$ 174.345,19; contribuição histórica de 10% (SECAP 2020, p. 27), 60 parcelas reais, desconto real de 6% a.a. Cenários fixos: e=0/λ=0; e=50%/λ=0; e=50%/λ=20%; e=100%/λ=0. Isenções e perdas são hipóteses, não médias nacionais. Perda somente sobre recebimentos dos pagantes, uma única vez.'),
    '2': spec('Intervalos das taxas nominais da linha financiada em 2026', 1,
        'Tabela de 2026; consulta do documento: 19/10/2026', '% nominal ao ano', 'Regras normativas · não são médias de contratos',
        '', 'Mínimo e máximo das células de renda, região e condição de cotista em cada faixa.',
        'Faixa 1: 4–5,25%; Faixa 2: 4,75–7%; Faixa 3: 7,66–8,16%; Classe Média: 10%. Não inclui TR, seguros e tarifas; não é CET ou retorno líquido do FGTS. Não aplicar retroativamente.'),
    '3': spec('Número de operações da linha financiada (FGTS e Fundo Social) por faixa, 2023–2026', 1,
        '2023–2026; 2026 parcial até 24/07', 'Mil operações financiadas', 'Dados observados · agregação administrativa',
        'exploracao_contratos', 'Contagem de operações por ano e código de faixa / 1.000.',
        'FGTS e Fundo Social; exclui OGU/FAR/FDS. Operações não são famílias únicas ou entregas. Os tetos de renda e a interpretação dos códigos mudam ao longo do tempo.'),
    '4': spec('Valor médio dos contratos por faixa, 2023–2026', 1,
        '2023–2026; 2026 parcial até 24/07', 'R$ mil correntes por operação', 'Dados observados · média ponderada',
        'exploracao_contratos', 'Soma do valor financiado / operações com valor de financiamento observado / 1.000, por ano e faixa.',
        'Mesmo universo da Figura 3. Principal reembolsável, não subsídio nem preço do imóvel. O DOCX contém legenda e fonte, mas não imagem para esta figura; reprodução pela definição e base citadas.'),
    '5': spec('Financiamento do MCMV por fonte e por ano com as mudanças do Programa, 2009–2026', 1,
        '2009–2026; 2026 parcial (financiada 24/07; subsidiada 30/06)', 'R$ bilhões correntes contratados', 'Dados observados · OGU aproximado por empreendimentos',
        'financiamento_por_fonte_ano', 'Soma dos valores de contratação por ano e fonte / 10⁹.',
        'OGU é proxy de empreendimentos subsidiados, não execução orçamentária. Ausência não comprova gasto zero. Crédito contratado não é subsídio. Marcos históricos não identificam causalidade.'),
    '6': spec('Arrecadação e saques em depósitos vinculados do FGTS, 2020–2025', 2,
        '2020–2025', 'R$ bilhões correntes', 'Dados observados · DFC Controladora',
        'arrecadacao_saques_fgts', 'Valores da DFC em R$ milhares / 10⁶.',
        'Arrecadação de 2020 exclui transferência extraordinária PIS/PASEP. Arrecadação menos saques não é lucro nem variação total do caixa.'),
    '7': spec('Caixa e patrimônio líquido do FGTS, 2020–2025', 2,
        'Saldos de encerramento de 2020–2025', 'R$ bilhões correntes', 'Dados observados · Balanço Controladora',
        'balanco_fgts', 'Caixa e equivalentes e patrimônio líquido em R$ milhares / 10⁶.',
        '2021–2022 reapresentados nas DF 2023. Patrimônio líquido não é disponibilidade de caixa; não somar os estoques como capacidade de financiamento.'),
    '8': spec('Déficit habitacional nacional e mudanças de base estatística', 4,
        '2007–2024; 2020–2021 sem estimativa nesta série', 'Milhões de domicílios', 'Estimativas publicadas · metodologias distintas',
        'deficit_fjp_historico', 'Totais nacionais publicados / 10⁶; linhas somente dentro de trechos comparáveis.',
        'Pnad anual 2007–2015; Censo 2010 isolado; PnadC reponderada 2016–2019; pontos 2022–2024 isolados pelas mudanças nos improvisados. Anos sem dado não são zero nem interpolados. Não identifica efeito causal do MCMV.'),
    '9': spec('Composição do déficit habitacional em 2022 e 2024', 4,
        'Edições de referência 2022 e 2024', 'Milhões de domicílios', 'Estimativas publicadas · componentes de cada edição',
        'deficit_fjp_componentes_2022_2024', 'Habitação precária + coabitação + ônus excessivo com aluguel, cada componente da respectiva edição / 10⁶.',
        'Não aplicar proporções de 2022 ao total de 2024. A comparação não separa mudança real de mudança na mensuração dos improvisados.'),
    '10': spec('Retorno da carteira habitacional e diferencial bruto frente à Selic', 2,
        '2021–2025', '% a.a. no painel A; R$ bilhões correntes no painel B', 'Dados contábeis e cenário de oportunidade bruto',
        'custo_oportunidade_fgts', 'Saldo médio = (abertura + encerramento)/2. Retorno = receita/saldo médio. Selic = [Π(1+taxa mensal)−1]. Diferencial = saldo médio × Selic − receita.',
        'Carteira habitacional inteira, não exclusivamente MCMV. Inclui juros, encargos e atualização monetária. Preservar diferencial negativo de 2021. Selic não é alternativa equivalente em risco e prazo. Não é despesa de caixa; não somar aos descontos/equalização.'),
    '11': spec('Variação efetiva do caixa e fluxo de manutenção', 6,
        'DFC 2023–2025', 'R$ bilhões de dezembro de 2025', 'DFC observada e fluxo de manutenção calculado',
        'sim_dfc_reconciliacao sim_ipca_mensal', 'Variação efetiva = caixa final − inicial. Manutenção = depósitos − saques + operacional + juros de títulos + outros investimentos. Fator = IPCA dez./2025 / média mensal anual.',
        'Manutenção exclui transferência PIS/PASEP, resgates líquidos de principal e recebimentos de investimentos permanentes. Mantém juros recebidos; não duplicar totais e rubricas da DFC.'),
    '12': spec('Saldos indicativos sob fluxos reais constantes', 6,
        '2025–2040; fluxos calibrados em 2023–2025', 'R$ bilhões de dezembro de 2025', 'Cenários calculados · teste de esforço',
        'sim_trajetorias sim_sustentabilidade sim_parametros', 'Saldo(t) = 33,466156 + (ano−2025) × fluxo anual real do cenário.',
        'Sete cenários: média 2023–2025; repetição de 2025; depósitos −5%; saques +5%; recebimentos −5%; choques combinados; liberações e descontos +10%. Choques permanentes sobre a média; fluxos reais constantes. Região negativa é financiamento não coberto, não operação efetiva com caixa negativo ou previsão de insolvência.'),
    '13': spec('Ajuste anual necessário para preservar o caixa real', 6,
        'Fluxos calibrados em 2023–2025; ajuste anual permanente', 'R$ bilhões de dezembro de 2025 por ano', 'Cenários calculados · mesmos sete da Figura 12',
        'sim_sustentabilidade', 'Ajuste anual = máximo(0, −fluxo anual do cenário).',
        'Preservar caixa difere de consumir reserva inicial. Ajuste pode ser recurso externo ou mudança nos fluxos; não é transferência da União já autorizada. Abrange todo o FGTS.'),
    '14': spec('Escala anual média no horizonte de dez anos', 6,
        'Estoque FJP 2024; horizonte ilustrativo de 10 anos', 'R$ bilhões de dezembro de 2025 por ano', 'Cenário calculado · escala de contratação',
        'sim_escala sim_parametros', 'Para cada recorte, N × 50% × parâmetro unitário / 10 anos. Parâmetros: FAR bruto 2024–2025; principal e subsídio FGTS F1 2023–2025.',
        'Comparação dos dois recortes: total e sem ônus com aluguel. 50% FAR/50% FGTS; focalização 100%. Três medidas separadas: FAR bruto, crédito reembolsável e subsídio registrado. Divisão aritmética não é cronograma de caixa nem VP; custo líquido FAR fica na Figura 1A e no simulador. Custo econômico integrado da financiada permanece pendente.'),
}


def read(name):
    return pd.read_csv(DATA / f'{name}.csv')


def parameters():
    return json.loads((DATA / 'sim_parametros.json').read_text(encoding='utf-8'))


def figure_data(number):
    """Dados exatos usados no gráfico e no download, sem depender da sessão UI."""
    if number == '1A':
        gross = parameters()['far_unitario_rs']
        scenarios = [('Referência: sem isenção, sem perda', 0., 0.),
                     ('50% isentos; sem perda', .5, 0.),
                     ('50% isentos; perda de 20%', .5, .2), ('100% isentos', 1., 0.)]
        return pd.DataFrame([{'Cenário':label, 'Isentos (%)':e*100,
            'Perda dos pagantes (%)':loss*100, 'Desconto real (% a.a.)':6.,
            'Parcelas reais':60, 'Contribuição total (%)':10., 'Valor bruto (R$)':gross,
            'Recebimentos em VP (R$)':gross-far_subsidy(gross,e,loss),
            'Subsídio líquido (R$)':far_subsidy(gross,e,loss),
            'Subsídio líquido (R$ mil)':far_subsidy(gross,e,loss)/1000}
            for label,e,loss in scenarios])
    if number == '2':
        base = tabela_taxas()
        return pd.DataFrame([{'Faixa':f,
            'Mínimo (% a.a.)':base.loc[base.Faixa.eq(f),COLUNAS_TAXAS].min().min(),
            'Máximo (% a.a.)':base.loc[base.Faixa.eq(f),COLUNAS_TAXAS].max().max()}
            for f in FAIXAS])
    if number in {'1','3','4'}:
        d = read('exploracao_contratos')
        d = d[d.ano.between(2023,2025 if number=='1' else 2026) & d.fonte.isin(['FGTS','Fundo Social'])].copy()
        d['Faixa'] = d.faixa_codigo.map(lambda x:f'Faixa {x}')
        keys = ['Faixa'] if number=='1' else ['ano','Faixa']
        g = d.groupby(keys,as_index=False).sum(numeric_only=True)
        g['Subsídio registrado (R$ por contrato)'] = g.subsidio_total / g.contratos_subsidio_observado.replace(0,float('nan'))
        g['Mil operações'] = g.contratos/1000
        g['R$ mil por operação'] = g.financiamento/g.financiamento_observado.replace(0,float('nan'))/1000
        return g
    if number == '5':
        d=read('financiamento_por_fonte_ano');d=d[d.ano.between(2009,2026)].copy()
        d['Fonte']=d.fonte.replace({'OGU':'Empreendimentos subsidiados (proxy OGU)'})
        d['R$ bilhões correntes']=d.valor_total_financiado/1e9
        return d
    if number == '6':
        d=read('arrecadacao_saques_fgts');d=d[d.ano.between(2020,2025)]
        d=d.melt(id_vars='ano',value_vars=['arrecadacao_rs_milhares','saques_rs_milhares'],var_name='Medida',value_name='R$ milhares correntes')
        d['Medida']=d.Medida.map({'arrecadacao_rs_milhares':'Arrecadação','saques_rs_milhares':'Saques'})
        d['R$ bilhões correntes']=d['R$ milhares correntes']/1e6
        return d
    if number == '7':
        d=read('balanco_fgts');d=d[d.ano.between(2020,2025)&d.rubrica.isin(['Caixa e equivalentes','Patrimônio líquido'])].copy()
        d['R$ bilhões correntes']=d.valor_rs_milhares/1e6
        return d
    if number == '8':
        d=read('deficit_fjp_historico');d=d[d.ano.between(2007,2024)].copy()
        d['Trecho']=d.serie_metodologica
        d.loc[d.ano.between(2016,2019),'Trecho']='PnadC reponderada · 2016–2019'
        d.loc[d.ano>=2022,'Trecho']='2022–2024 · mudanças nos improvisados'
        d['Milhões de domicílios']=d.deficit_domicilios/1e6
        return d
    if number == '9':
        d=read('deficit_fjp_componentes_2022_2024')
        d['Milhões de domicílios']=d.deficit_domicilios/1e6
        return d
    if number == '10':
        d=read('custo_oportunidade_fgts').copy()
        d['Diferencial bruto (R$ bi)']=(d.saldo_medio_rs_milhares*d.selic_pct_ano/100-d.receita_rs_milhares)/1e6
        return d
    if number == '11':
        d=read('sim_dfc_reconciliacao')
        return d
    if number == '12':
        return read('sim_trajetorias').merge(read('sim_sustentabilidade').query('horizonte == 15')[['cenario','fluxo_anual_bi']],on='cenario',validate='many_to_one')
    if number == '13':
        return read('sim_sustentabilidade').query('horizonte == 15').copy()
    if number == '14':
        d=read('sim_escala')
        return d[(d.ano_deficit==2024)&(d.modalidade=='50% FAR / 50% FGTS')&(d.focalizacao==1)&(d.horizonte==10)].copy()
    raise KeyError(number)


def build_figure(number, d=None):
    d=figure_data(number) if d is None else d
    if number == '1A':
        gross=d['Valor bruto (R$)'].iloc[0]
        fig=go.Figure(go.Bar(y=d['Cenário'],x=d['Subsídio líquido (R$ mil)'],orientation='h',
            marker_color=['#184f63','#467b89','#78a4ab','#c1d4d7'],
            text=[f'{v:.1f}'.replace('.',',') for v in d['Subsídio líquido (R$ mil)']],
            textposition='outside',cliponaxis=False))
        fig.add_vline(x=gross/1000,line_dash='dash',line_color='#c58341')
        fig.update_layout(title='Valor bruto por unidade: R$ 174,3 mil',
            xaxis_title='Subsídio líquido estimado · R$ mil de dez./2025',
            yaxis=dict(autorange='reversed'),xaxis=dict(range=[0,gross/1000*1.15]))
        return fig
    if number == '2':
        fig=go.Figure()
        for i,row in d.iterrows():
            fig.add_trace(go.Scatter(x=[row['Mínimo (% a.a.)'],row['Máximo (% a.a.)']],
                y=[row.Faixa]*2,mode='lines+markers',name=row.Faixa,
                line=dict(width=8,color=COLORS[i]),showlegend=False))
        fig.update_xaxes(title='Taxa nominal (% a.a.)',range=[3.5,11])
        fig.update_yaxes(autorange='reversed')
        return fig
    if number == '1':
        fig=px.bar(d,x='Faixa',y='Subsídio registrado (R$ por contrato)',text_auto='.2s')
    elif number in {'3','4'}:
        fig=px.bar(d,x='ano',y='Mil operações' if number=='3' else 'R$ mil por operação',color='Faixa',barmode='group')
    elif number == '5':
        fig=px.bar(d,x='ano',y='R$ bilhões correntes',color='Fonte')
        for year,label in [(2009,'Criação'),(2011,'Fase 2'),(2016,'Fase 3'),(2020,'CVA'),(2023,'Retomada'),(2025,'Fundo Social')]:
            fig.add_vline(x=year,line_dash='dot',annotation_text=label,annotation_textangle=-90)
    elif number == '6':
        fig=px.bar(d,x='ano',y='R$ bilhões correntes',color='Medida',barmode='group')
    elif number == '7':
        fig=px.bar(d,x='ano',y='R$ bilhões correntes',color='rubrica',barmode='group')
    elif number == '8':
        fig=go.Figure()
        for i,(name,g) in enumerate(d.groupby('Trecho',sort=False)):
            if name.startswith('Pnad anual'):
                # Não unir a linha da PNAD através do ponto isolado do Censo.
                xs=[];ys=[]
                for year in range(int(g.ano.min()),int(g.ano.max())+1):
                    v=g[g.ano==year];xs.append(year);ys.append(None if v.empty else v['Milhões de domicílios'].iloc[0])
                mode='lines+markers'
            else:
                xs=g.ano;ys=g['Milhões de domicílios']
                mode='lines+markers' if name.startswith('PnadC reponderada') else 'markers'
            fig.add_trace(go.Scatter(x=xs,y=ys,mode=mode,name=name,connectgaps=False,marker_color=COLORS[i]))
        fig.add_vrect(x0=2019.5,x1=2021.5,fillcolor='#dde3eb',opacity=.5,line_width=0,
            annotation_text='Sem estimativa',annotation_position='top left')
        fig.update_xaxes(title='Ano',tickmode='array',tickvals=list(range(2007,2025)))
        fig.update_yaxes(title='Milhões de domicílios')
    elif number == '9':
        d=d.copy();d['Ano']=d.ano.astype(str)
        fig=px.bar(d,x='Ano',y='Milhões de domicílios',color='componente',text_auto='.2f',
            color_discrete_sequence=['#173e59','#137d81','#c58341'])
    elif number == '10':
        fig=make_subplots(rows=1,cols=2,subplot_titles=['A · Retorno e Selic','B · Diferencial bruto'])
        fig.add_trace(go.Bar(x=d.ano,y=d.retorno_contabil_bruto_pct,name='Carteira habitacional'),row=1,col=1)
        fig.add_trace(go.Bar(x=d.ano,y=d.selic_pct_ano,name='Selic composta'),row=1,col=1)
        fig.add_trace(go.Bar(x=d.ano,y=d['Diferencial bruto (R$ bi)'],name='Diferencial bruto',marker_color=['#137d81' if v<0 else '#173e59' for v in d['Diferencial bruto (R$ bi)']]),row=1,col=2)
        fig.update_yaxes(title='% ao ano',row=1,col=1)
        fig.update_yaxes(title='R$ bilhões correntes',row=1,col=2)
        fig.update_xaxes(dtick=1)
    elif number == '11':
        g=d[['ano','delta_real_bi','maintenance_real_bi']].rename(columns={'delta_real_bi':'Variação efetiva do caixa','maintenance_real_bi':'Fluxo de manutenção'}).melt(id_vars='ano',var_name='Medida',value_name='R$ bilhões de dez./2025')
        fig=px.bar(g,x='ano',y='R$ bilhões de dez./2025',color='Medida',barmode='group')
    elif number == '12':
        fig=px.line(d,x='ano',y='saldo_indicativo_bi',color='cenario',labels={'saldo_indicativo_bi':'Saldo indicativo · R$ bi de dez./2025','ano':'Ano','cenario':'Cenário'})
        fig.update_xaxes(tickmode='array',tickvals=[2025,2030,2035,2040])
        fig.add_hline(y=0,line_dash='dot')
    elif number == '13':
        fig=px.bar(d,x='aporte_anual_preserva_caixa_bi',y='cenario',orientation='h',color='cenario',text_auto='.2f',
            labels={'aporte_anual_preserva_caixa_bi':'R$ bilhões de dez./2025 por ano','cenario':'Cenário'})
        fig.update_yaxes(autorange='reversed');fig.update_layout(showlegend=False)
    elif number == '14':
        g=d.melt(id_vars='recorte',value_vars=['far_anual_bi','credito_anual_bi','subsidio_anual_bi'],var_name='Medida',value_name='R$ bilhões de dez./2025 por ano')
        g['Medida']=g.Medida.map({'far_anual_bi':'FAR: valor bruto','credito_anual_bi':'FGTS: crédito','subsidio_anual_bi':'Subsídio registrado'})
        fig=px.bar(g,x='recorte',y='R$ bilhões de dez./2025 por ano',color='Medida',barmode='group',
            labels={'recorte':'Recorte do déficit'},color_discrete_sequence=['#173e59','#c58341','#137d81'])
    else:
        raise KeyError(number)
    return fig


def source_links(number):
    if number == '2':
        return [('Ministério das Cidades · tabela normativa de 2026',FONTE)]
    links=[]
    for name in FIGURES[number]['bases']:
        meta=json.loads((DATA/f'{name}.meta.json').read_text(encoding='utf-8'))
        for base in meta.get('bases',[]):
            pair=(base['nome'],base['url'])
            if pair not in links:
                links.append(pair)
    if number=='1A':
        links.append(('SECAP (2020), p. 27 · contribuição histórica de 10%',
            'https://www.gov.br/cgu/pt-br/assuntos/noticias/2021/04/cgu-divulga-prestacao-de-contas-do-presidente-da-republica-de-2020/relatorio-de-avaliacao-pmcmv.pdf'))
    if number in {'11','12','13','14'}:
        for year in (2023,2025):
            suffix='-v6' if year==2023 else ''
            links.append((f'FGTS · DF {year}, DFC Controladora',
                f'https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_{year}{suffix}.pdf'))
        links.append(('IBGE · IPCA mensal, SIDRA 1737',
            'https://api.sidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/202301-202512'))
    if number=='14':
        for name in ('deficit_fjp_componentes_2022_2024','exploracao_contratos','far_anual'):
            meta=json.loads((DATA/f'{name}.meta.json').read_text(encoding='utf-8'))
            links.extend((b['nome'],b['url']) for b in meta.get('bases',[]))
    return links


def render_figure(number, key_prefix='dissertation'):
    s=FIGURES[number];key=f'{key_prefix}_figure_{number}'
    st.subheader(f'Figura {number} — {s["title"]}')
    st.caption(f'{s["kind"]} · Período: {s["period"]} · Unidade: {s["unit"]}')
    d=figure_data(number)
    plot(build_figure(number,d),key)
    if number=='1A':
        st.latex(r'S = V - (1-e)(1-\lambda)\sum_{m=1}^{60}\frac{0{,}10V/60}{(1+0{,}06)^{m/12}}')
    st.write('**Fórmula / construção:** '+s['formula'])
    st.caption('Hipóteses e limites: '+s['assumptions'])
    st.markdown('**Fonte:** '+' · '.join(f'[{name}]({url})' for name,url in source_links(number)))
    table(d,key)
    st.caption('Referência: Dissertacao_FAR_Revisada.docx · inventário completo e ressalvas em docs/graficos_dissertacao.md.')


def render_index(navigate):
    st.header('Gráficos da dissertação')
    st.write('15 figuras da revisão FAR, com o recorte do documento, fontes, hipóteses e dados para download. Selecione uma figura para abrir sua reprodução na seção correspondente.')
    for page,title in SECTIONS.items():
        with st.expander(title,expanded=True):
            for number,s in FIGURES.items():
                if s['page']==page:
                    st.button(f'Figura {number} — {s["title"]}',key=f'figure_open_{number}',
                        on_click=navigate,args=(page,number),use_container_width=True)
    st.caption('Conferência: nenhuma figura pendente de reprodução. A Figura 4 não tem imagem embutida no DOCX; foi reproduzida pela legenda e base citadas. Custo integrado da linha financiada permanece sem mensuração, como no documento.')


def render_section(page):
    choices=[n for n,s in FIGURES.items() if s['page']==page]
    if not choices:
        return
    st.header('Gráficos da dissertação · reprodução de referência')
    st.caption('Recortes fixos do documento. Os controles exploratórios abaixo continuam disponíveis e não alteram estas figuras.')
    number=st.selectbox('Figura do documento',choices,
        format_func=lambda n:f'Figura {n} — {FIGURES[n]["title"]}',key=f'dissertation_selection_{page}')
    render_figure(number)
    st.divider()
