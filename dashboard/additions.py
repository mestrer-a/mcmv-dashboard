"""Figuras da v09 e complementos; apenas agregações de bases identificadas."""
import pandas as pd
import plotly.express as px
import streamlit as st
from ui import DATA,COLORS,plot,table
from periods import period

def read(name):return pd.read_csv(DATA/f'{name}.csv')
def br(x,dec=1):return f'{x:,.{dec}f}'.replace(',','X').replace('.',',').replace('X','.')
FAIXAS={str(i):f'Faixa {i}' for i in range(1,5)}
PALETTE={f'Faixa {i}':COLORS[i-1] for i in range(1,5)}
PALETTE['Sem classificação']='#65778A'

def by_faixa(d):
    d=d.copy();d['Faixa']=d.faixa_codigo.astype(str).map(FAIXAS).fillna('Sem classificação')
    return d.groupby('Faixa',as_index=False).sum(numeric_only=True)

def dissertation_charts():
    st.header('Fase atual do programa · figuras da dissertação')
    st.subheader('Subsídio registrado por contrato financiado e faixa')
    d=period(read('exploracao_contratos'),'doc_subsidy',True,default=(2023,2025))
    if not d.empty:
        a=by_faixa(d);a['R$ por contrato']=a.subsidio_total/a.contratos_subsidio_observado.replace(0,float('nan'))
        a['Rótulo']=a['R$ por contrato'].map(lambda v:'R$ '+br(v/1000)+' mil')
        fig=px.bar(a,x='Faixa',y='R$ por contrato',text='Rótulo',color_discrete_sequence=[COLORS[0]])
        fig.update_traces(textposition='outside',cliponaxis=False);fig.update_yaxes(rangemode='tozero')
        if a['R$ por contrato'].max()>0:fig.update_yaxes(range=[0,a['R$ por contrato'].max()*1.15])
        plot(fig,'doc_subsidy');table(a,'doc_subsidy')
        st.caption('Figura 1 da v09 · padrão 2023–2025. Média ponderada: soma das quatro rubricas registradas / contratos com rubricas completas. '
                   'FAR fica fora desta figura. Desconto e equilíbrio são campos distintos; esta soma não mede o benefício total de taxa.')
        st.subheader('Desconto e equilíbrio dentro do subsídio registrado')
        r=read('subsidio_rubricas_ano');r=r[r.ano.isin(d.ano)]
        r=r.groupby('faixa_codigo',as_index=False).sum(numeric_only=True)
        n=d.groupby('faixa_codigo').contratos_subsidio_observado.sum()
        fields=[x for x in r.columns if x.startswith('vlr_subsidio')]
        for field in fields:r[field]=r[field]/r.faixa_codigo.map(n).replace(0,float('nan'))
        m=r.melt(id_vars='faixa_codigo',value_vars=fields,var_name='Rubrica',value_name='R$ por contrato')
        m['Faixa']=m.faixa_codigo.astype(str).map(FAIXAS).fillna('Sem classificação')
        m['Rubrica']=m.Rubrica.str.replace('vlr_subsidio_','').str.replace('_',' ').str.upper()
        plot(px.bar(m,x='Faixa',y='R$ por contrato',color='Rubrica',color_discrete_sequence=COLORS),'doc_rubrics');table(m,'doc_rubrics')
        st.caption('Mesmo período e denominador da figura anterior. A soma inclui desconto e equilíbrio; não deve ser descrita integralmente como desconto direto no principal. '
                   'Os campos administrativos não substituem uma estimação do benefício de taxa contra benchmark.')
    st.subheader('Operações financiadas por faixa')
    c=period(read('exploracao_contratos'),'doc_profile',True,default=(2023,2026))
    if c.empty:return
    c['Faixa']=c.faixa_codigo.astype(str).map(FAIXAS).fillna('Sem classificação')
    a=c.groupby(['ano','Faixa'],as_index=False).sum(numeric_only=True)
    a['Mil operações']=a.contratos/1000
    plot(px.bar(a,x='ano',y='Mil operações',color='Faixa',barmode='group',color_discrete_map=PALETTE),'doc_profile');table(a,'doc_profile')
    st.caption('Figura 2 da v09 · FGTS e Fundo Social; somente operações financiadas. 2026 parcial. '
               'Códigos históricos de faixa não são bandas de renda constantes e não incluem o FAR.')
    st.subheader('Valor médio financiado por operação e faixa')
    a['R$ mil por operação']=a.financiamento/a.financiamento_observado.replace(0,float('nan'))/1000
    fig=px.line(a,x='ano',y='R$ mil por operação',color='Faixa',markers=True,color_discrete_map=PALETTE)
    plot(fig,'doc_ticket');table(a,'doc_ticket')
    st.caption('Figura 3 da v09 · mesmo recorte do gráfico de operações acima. Soma financiada / operações com valor observado. '
               'Principal mobilizado, não preço do imóvel nem custo econômico.')

def far_comparison():
    st.subheader('Atendimento registrado à Faixa 1 por modalidade')
    d=period(read('faixa1_modalidade'),'modalities',True,default=(2023,2026))
    if d.empty:return
    t=d.groupby(['ano','modalidade','unidade'],as_index=False).volume.sum()
    t['Mil registros']=t.volume/1000
    fig=px.bar(t,x='ano',y='Mil registros',color='modalidade',barmode='group',hover_data=['unidade','volume'],
               color_discrete_sequence=[COLORS[0],COLORS[1]])
    # Short legend; full universe stays in the visible note and table.
    for tr in fig.data:
        tr.name='Financiada · operações' if 'financiada' in tr.name else 'FAR · unidades contratadas'
    plot(fig,'faixa1_modalidade');table(t,'faixa1_modalidade')
    st.caption('Financiada: código 1, FGTS/FS, contagem de operações por assinatura. FAR/OGU (proxy): modalidade FAR, '
               'soma de qtd_uh por dt_assinatura; inclui a situação contratual registrada, sem descontar distratos. '
               'Operações e UH não são medidas idênticas e não são somadas. FAR não esgota a linha subsidiada. '
               '2026 parcial: financiado até 24/07 e subsidiado até 30/06. Não mede entregas ou déficit eliminado.')
    far_years=set(d.loc[d.modalidade.str.contains('subsidiada'),'ano'])
    missing=sorted(set(d.ano)-far_years)
    if missing:st.info('Sem registros FAR por assinatura em '+', '.join(map(str,missing))+'. Ausência nesta extração não comprova ausência de atuação ou gasto público.')

def legacy_subsidy():
    st.subheader('Valor registrado por unidade e faixa · comparação histórica')
    d=period(read('exploracao_contratos'),'legacy_subsidy',True,default=(2009,2026))
    if d.empty:return
    a=by_faixa(d);a['Valor por registro']=a.subsidio_total/a.contratos_subsidio_observado.replace(0,float('nan'))
    a['Medida']='Subsídio registrado por operação'
    far=read('far_anual');far=far[far.ano.between(d.ano.min(),d.ano.max())]
    if not far.empty and far.qtd_uh.sum():
        a=pd.concat([pd.DataFrame([{'Faixa':'FAR · proxy Faixa 1','Valor por registro':far.val_contratado_total.sum()/far.qtd_uh.sum(),'Medida':'Valor contratado por UH'}]),a],ignore_index=True)
    plot(px.bar(a,x='Valor por registro',y='Faixa',color='Medida',orientation='h',color_discrete_sequence=COLORS),'subsidy');table(a,'subsidy')
    st.caption('Exploração anterior preservada, agora recalculável por período. FAR: valor bruto por UH; financiadas: subsídio registrado por operação. '
               'Conceitos diferentes, sem soma nem interpretação como ranking de custo econômico. Ausências não são zeros.')

FJP_LABELS={'faixa_1':'Faixa 1 · até R$ 2.640','faixa_2':'Faixa 2 · até R$ 4.400',
            'faixa_3':'Faixa 3 · até R$ 8.000','acima_faixa_3':'Acima de R$ 8.000'}
COMP={'precaria':'Habitação precária','coabitacao':'Coabitação','onus_aluguel':'Ônus com aluguel'}
FJP_NOTE=('FJP, referência 2022, tabelas 4–5 (p. 30–32), transcrição fornecida pelo autor e preservada. '
          'Déficit é dado de entrada; não recalculado a partir de contratos. Faixas em R$ classificadas pela FJP '
          'segundo os limites citados na edição, sem equivalência automática aos códigos dos contratos atuais. '
          'Não aplicar estas proporções ao total de 2024. Totais impressos podem divergir por poucos domicílios das somas.')

def deficit_charts():
    st.header('Déficit por renda e componente · edição 2022')
    d=read('deficit_fjp_faixa_componente')
    st.selectbox('Edição com abertura disponível nesta base',[2022],key='fjp_edition')
    territory=st.selectbox('Território dos gráficos de déficit',d.territorio.unique().tolist(),index=list(d.territorio.unique()).index('Brasil'))
    st.info('Os recortes de governo se aplicam às séries de contratos. Os gráficos FJP abaixo mantêm a referência 2022: '
            'é a única edição com abertura integrada neste repositório. O total nacional de 2024 (5.773.983) é contexto de outra edição, sem repartição por renda/componente aqui.')
    t=d[d.territorio.eq(territory)].copy()
    totals=t[(t.componente=='deficit_total')&(t.faixa!='total')].copy()
    denominator=t[(t.componente=='deficit_total')&(t.faixa=='total')].deficit_domicilios.iloc[0]
    low=totals.loc[totals.faixa.eq('faixa_1'),'deficit_domicilios'].iloc[0]
    rent=t.loc[t.componente.eq('onus_aluguel')&t.faixa.eq('total'),'deficit_domicilios'].iloc[0]
    for col,label,value in zip(st.columns(3),['Déficit · '+territory,'Faixa 1 no déficit','Ônus com aluguel no déficit'],
                               [br(denominator,0),br(100*low/denominator)+'%',br(100*rent/denominator)+'%']):col.metric(label,value)
    totals['Faixa']=totals.faixa.map(FJP_LABELS);totals['Milhões de domicílios']=totals.deficit_domicilios/1e6
    totals['Participação (%)']=100*totals.deficit_domicilios/denominator
    totals['Rótulo']=totals['Participação (%)'].map(lambda v:br(v)+'%')
    st.subheader(f'Déficit por faixa de renda · {territory}')
    plot(px.bar(totals,x='Faixa',y='Milhões de domicílios',text='Rótulo',color_discrete_sequence=[COLORS[0]]),'fjp_faixa');table(totals,'fjp_faixa');st.caption(FJP_NOTE)
    components=t[(t.componente!='deficit_total')&(t.faixa!='total')].copy()
    components['Faixa']=components.faixa.map(FJP_LABELS);components['Componente']=components.componente.map(COMP)
    components['Milhões de domicílios']=components.deficit_domicilios/1e6
    st.subheader('Quais componentes formam o déficit de cada faixa?')
    plot(px.bar(components,x='Faixa',y='Milhões de domicílios',color='Componente',color_discrete_sequence=COLORS),'fjp_components');table(components,'fjp_components');st.caption(FJP_NOTE)
    st.subheader('Déficit total e recorte sem ônus com aluguel')
    cut=totals[['faixa','Faixa','deficit_domicilios']].copy()
    rents=t[(t.componente=='onus_aluguel')&(t.faixa!='total')].set_index('faixa').deficit_domicilios
    cut['Déficit total']=cut.deficit_domicilios
    cut['Sem ônus com aluguel']=cut.deficit_domicilios-cut.faixa.map(rents)
    m=cut.melt(id_vars=['faixa','Faixa'],value_vars=['Déficit total','Sem ônus com aluguel'],var_name='Recorte',value_name='Domicílios');m['Milhões de domicílios']=m.Domicílios/1e6
    plot(px.bar(m,x='Faixa',y='Milhões de domicílios',color='Recorte',barmode='group',color_discrete_sequence=COLORS),'fjp_rent');table(m,'fjp_rent')
    st.caption(FJP_NOTE+' Sem ônus = total impresso menos ônus. Não equivale automaticamente a unidades a construir. '
               'O ônus é definido até 3 SM e aparece zerado nas duas bandas superiores da tabela; zero por definição não é ausência de dificuldade habitacional.')
    st.subheader('A concentração em baixa renda muda entre regiões?')
    regions=d[d.territorio.isin(['Norte','Nordeste','Sudeste','Sul','Centro-Oeste']) & d.componente.eq('deficit_total')].copy()
    den=regions[regions.faixa=='total'].set_index('territorio').deficit_domicilios
    regions=regions[regions.faixa!='total'];regions['Faixa']=regions.faixa.map(FJP_LABELS)
    regions['Participação (%)']=100*regions.deficit_domicilios/regions.territorio.map(den)
    plot(px.bar(regions,x='territorio',y='Participação (%)',color='Faixa',color_discrete_sequence=COLORS),'fjp_regions');table(regions,'fjp_regions');st.caption(FJP_NOTE+' Regiões são partições distintas do corte RM/demais áreas; não somar esses universos.')
    st.subheader('Contratos e subsídios registrados se concentram nas mesmas faixas?')
    c=period(read('exploracao_contratos'),'targeting',True,default=(2023,2025))
    if c.empty:return
    a=by_faixa(c);a['Contratos (%)']=100*a.contratos/a.contratos.sum();a['Subsídio registrado (%)']=100*a.subsidio_total/a.subsidio_total.sum() if a.subsidio_total.sum() else float('nan')
    m=a.melt(id_vars='Faixa',value_vars=['Contratos (%)','Subsídio registrado (%)'],var_name='Medida',value_name='%')
    plot(px.bar(m,x='Faixa',y='%',color='Medida',barmode='group',color_discrete_sequence=COLORS),'targeting');table(a,'targeting')
    st.caption('FGTS/FS, sem FAR. Confronto descritivo com o déficit, em universos e limites de renda diferentes. '
               'Não permite afirmar que a Faixa X elimina Y% do déficit, nem quantificar impacto de faixas superiores. '
               'Subsídio registrado zero não elimina eventual benefício de taxa.')

def budget_chart():
    st.subheader('Orçamento operacional inicial do FGTS · 2026')
    st.selectbox('Edição do orçamento',[2026],key='budget_edition')
    d=read('orcamento_operacional_2026');d['R$ bilhões']=d.valor_rs_milhares/1e6
    plot(px.bar(d,x='area',y='R$ bilhões',text='R$ bilhões',color_discrete_sequence=[COLORS[0]]),'budget');table(d,'budget')
    st.caption('Quadro 2 da v09 · Resolução CCFGTS 1.133/2025, orçamento inicial: contratação planejada, não execução nem caixa. '
               'Edição fixa, independente do recorte histórico. Não é uma consolidação de todas as reprogramações de 2026. '
               'Descontos são uma dotação separada: R$ 12,5 bi iniciais e R$ 13,0 bi após a suplementação divulgada em setembro.')
