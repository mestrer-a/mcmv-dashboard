"""Valor médio FAR observado e sua decomposição sob hipóteses explícitas."""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from far import far_subsidy
from ui import DATA, plot, table

SECAP='https://www.gov.br/cgu/pt-br/assuntos/noticias/2021/04/cgu-divulga-prestacao-de-contas-do-presidente-da-republica-de-2020/relatorio-de-avaliacao-pmcmv.pdf'
NAVY,TEAL='#173e59','#319b91'
GROSS='Valor bruto real por unidade (R$)'
NET='Subsídio em VP por unidade (R$)'
RET='Recebimentos em VP por unidade (R$)'
SIMPLE='Subsídio com abatimento direto de 10% (R$)'


def br(v,n=1):
    return f'{v:,.{n}f}'.replace(',','X').replace('.',',').replace('X','.')


def annual_history():
    annual=pd.read_csv(DATA/'far_anual.csv').set_index('ano')
    ipca=pd.read_csv(DATA/'far_ipca_mensal.csv',dtype={'mes':str})
    dec=float(ipca.loc[ipca.mes.eq('202512'),'indice'].iloc[0])
    # Preserva os parâmetros da dissertação: média mensal do ano, não inflação
    # na data de cada assinatura. 2026 usa somente janeiro–junho.
    factors=dec/ipca.groupby('ano').indice.mean()
    d=annual.reindex(range(2009,2027)).reset_index()
    d['Fator IPCA para dez./2025']=d.ano.map(factors)
    d['Meses no índice médio']=d.ano.map(ipca.groupby('ano').size())
    d['Valor bruto nominal por unidade (R$)']=d.val_contratado_total/d.qtd_uh
    d[GROSS]=d['Valor bruto nominal por unidade (R$)']*d['Fator IPCA para dez./2025']
    d[NET]=d[GROSS].apply(lambda v:far_subsidy(v) if pd.notna(v) else float('nan'))
    d[RET]=d[GROSS]-d[NET]
    d[SIMPLE]=.9*d[GROSS]
    d['Retorno com abatimento direto de 10% (R$)']=.1*d[GROSS]
    d['Situação']=d.qtd_uh.map(lambda v:'Sem registros nesta extração' if pd.isna(v) else 'Ano com registros')
    d.loc[d.ano.eq(2026),'Situação']='Parcial até 30/06/2026'
    return d


def cohort(history,period='2024–2025'):
    if period=='2009–2025':
        d=history[history.ano.between(2009,2025)]
    elif period=='2024–2025':
        d=history[history.ano.isin([2024,2025])]
    else:
        d=history[history.ano.eq(int(period))]
    d=d[d.qtd_uh.notna()]
    if d.empty or d.qtd_uh.sum()<=0:
        raise ValueError('Período sem unidades na extração')
    return float((d[GROSS]*d.qtd_uh).sum()/d.qtd_uh.sum()),int(d.qtd_uh.sum())


def reference_scenarios(gross):
    scenarios=[('Referência: sem isenção, sem perda',0.,0.),
        ('50% isentos; sem perda',.5,0.),('50% isentos; perda de 20%',.5,.2),('100% isentos',1.,0.)]
    return pd.DataFrame([{'Cenário':label,'Isentos (%)':e*100,'Perda dos pagantes (%)':loss*100,
        'Valor bruto (R$)':gross,'Recebimentos em VP (R$)':gross-far_subsidy(gross,e,loss),
        'Subsídio líquido (R$)':far_subsidy(gross,e,loss)} for label,e,loss in scenarios])


def summary_data():
    gross,n=cohort(annual_history(),'2024–2025')
    net=far_subsidy(gross)
    return pd.DataFrame([{'Modalidade':'FAR','Período':'2024–2025',
        'Unidades habitacionais':n,GROSS:gross,RET:gross-net,NET:net,
        'Base de preços':'dezembro de 2025','Contribuição hipotética (%)':10,
        'Parcelas reais':60,'Desconto real anual (%)':6,'Isenção (%)':0,'Perda (%)':0}])


def summary_figure(data=None):
    """Síntese por modalidade, na linguagem visual da Figura 1."""
    d=summary_data() if data is None else data
    net=float(d[NET].iloc[0])
    fig=go.Figure(go.Bar(x=d.Modalidade,y=d[NET],width=.4,
        marker_color='#1f77b4',text=['R$ '+br(net/1000)+' mil'],
        textposition='outside',cliponaxis=False,
        hovertemplate='FAR · média ponderada 2024–2025<br>Subsídio líquido estimado: R$ %{y:,.2f}<extra></extra>'))
    fig.update_layout(title='Subsídio líquido estimado por unidade FAR<br><sup>Média ponderada · 2024–2025</sup>',
        showlegend=False,meta={'kind':'far_period_mean','period':'2024–2025','net':net,
            'gross':float(d[GROSS].iloc[0]),'units':int(d['Unidades habitacionais'].iloc[0])})
    fig.update_xaxes(title='Modalidade',type='category')
    fig.update_yaxes(title='R$ por unidade · preços de dez./2025',range=[0,200000],
        tickmode='array',tickvals=[0,50000,100000,150000,200000],
        ticktext=['0','50 mil','100 mil','150 mil','200 mil'])
    return fig


def cost_figure(history=None,period='2024–2025',simple=False):
    d=annual_history() if history is None else history
    gross,_=cohort(d,period)
    net=.9*gross if simple else far_subsidy(gross)
    share=100*net/gross
    net_col=SIMPLE if simple else NET
    ret_col='Retorno com abatimento direto de 10% (R$)' if simple else RET
    subtitle='Abatimento direto de 10%, sem desconto temporal' if simple else '60 parcelas reais · desconto de 6% a.a. · sem isenções ou perdas'
    fig=make_subplots(rows=2,cols=1,row_heights=[.27,.73],vertical_spacing=.27,
        subplot_titles=[f'COMPOSIÇÃO POR UNIDADE · {period}',
                        'VALOR MÉDIO POR UNIDADE, POR ANO DE CONTRATAÇÃO'])
    fig.add_trace(go.Bar(x=[net/1000],y=[0],width=.75,orientation='h',name='Subsídio estimado',
        marker_color=NAVY,text=[f'<b>{br(share,0 if simple else 2)}% de subsídio</b>'],textposition='inside',
        insidetextanchor='middle',textfont=dict(size=22,color='white'),
        hovertemplate='Subsídio estimado: R$ %{x:.1f} mil<extra></extra>',showlegend=False),row=1,col=1)
    fig.add_trace(go.Bar(x=[(gross-net)/1000],y=[0],width=.75,orientation='h',name='Retorno hipotético',
        marker_color=TEAL,showlegend=False,
        hovertemplate='Retorno hipotético: R$ %{x:.1f} mil<extra></extra>'),row=1,col=1)
    fig.add_annotation(xref='x',yref='y',x=net/2000,y=0,text=f'R$ {br(net/1000)} mil',
        yshift=-61,showarrow=False,font=dict(color=NAVY,size=18))
    fig.add_annotation(xref='x',yref='y',x=(net+(gross-net)/2)/1000,y=0,
        text=f'<b>{br(100-share,0 if simple else 2)}% retornam</b><br>R$ {br((gross-net)/1000)} mil',
        yshift=70,xanchor='right',showarrow=False,font=dict(color='#23766d',size=16))
    fig.update_xaxes(range=[0,gross/1000*1.03],showticklabels=False,showgrid=False,zeroline=False,row=1,col=1)
    fig.update_yaxes(range=[-.8,.8],showticklabels=False,showgrid=False,zeroline=False,row=1,col=1)
    valid=d[d.qtd_uh.notna()]
    custom=valid[['qtd_uh',GROSS]].to_numpy()
    fig.add_trace(go.Bar(x=valid.ano,y=valid[net_col]/1000,name='Subsídio estimado',
        marker_color=NAVY,customdata=custom,
        hovertemplate='%{x}<br>Subsídio: R$ %{y:.1f} mil por unidade<br>Unidades: %{customdata[0]:,.0f}<br>Valor bruto: R$ %{customdata[1]:,.2f}<extra></extra>'),row=2,col=1)
    fig.add_trace(go.Bar(x=valid.ano,y=valid[ret_col]/1000,name='Retorno hipotético',
        marker_color=TEAL,hovertemplate='%{x}<br>Retorno: R$ %{y:.1f} mil por unidade<extra></extra>'),row=2,col=1)
    fig.add_vrect(x0=2019.5,x1=2023.5,line_width=0,fillcolor='#e7ebef',opacity=.7,layer='below',row=2,col=1)
    fig.add_annotation(xref='x2',yref='y2',x=2021.5,y=float(valid[GROSS].max()/1000)*.55,
        text='2020–2023<br><b>Sem registros<br>nesta extração</b>',showarrow=False,
        font=dict(size=14,color='#61727d'))
    # Distingue o corte parcial sem sugerir queda de custo por efeito do programa.
    fig.add_vrect(x0=2025.55,x1=2026.45,line_width=0,fillcolor='#fbf1e3',opacity=.55,layer='below',row=2,col=1)
    fig.update_xaxes(tickmode='array',tickvals=list(range(2009,2027)),
        ticktext=[str(y)+('*' if y==2026 else '') for y in range(2009,2027)],tickangle=-45,
        range=[2008.4,2026.6],row=2,col=1)
    fig.update_yaxes(title='R$ mil por unidade · dez./2025',rangemode='tozero',row=2,col=1)
    fig.update_layout(barmode='stack',bargap=.3,hovermode='closest',legend_traceorder='normal',
        meta={'period':period,'simple':simple,'gross':gross,'net':net,'share':share},
        title=dict(text=subtitle,font=dict(size=14,color='#61727d')))
    return fig


def render_history(key_prefix):
    history=annual_history()
    default,_=cohort(history)
    st.write('**Mesmo com recuperação integral da contribuição hipotética de 10%, a maior parte do valor da unidade continua sendo subsídio.** O gráfico separa essas duas parcelas e mostra sua escala no histórico disponível.')
    c1,c2=st.columns([1,1])
    period=c1.selectbox('Período em destaque',['2024–2025','2009–2025']+[str(y) for y in history.loc[history.qtd_uh.notna(),'ano']],
        format_func=lambda p:p+(' · referência da dissertação' if p=='2024–2025' else ' · anos com registros' if p=='2009–2025' else ' · parcial' if p=='2026' else ''),key=key_prefix+'_period')
    simple=c2.selectbox('Tratamento dos recebimentos',[False,True],
        format_func=lambda x:'Abatimento direto de 10% · sem desconto temporal' if x else 'Valor presente · hipótese da dissertação',key=key_prefix+'_method')
    gross,n=cohort(history,period);net=.9*gross if simple else far_subsidy(gross)
    for col,label,value in zip(st.columns(3),['Valor contratado / unidade','Retorno hipotético / unidade','Subsídio estimado / unidade'],[gross,gross-net,net]):
        col.metric(label,'R$ '+br(value,2))
    st.caption(f'Média ponderada por {br(n,0)} unidades no período em destaque. A unidade de comparação é a moradia, não o empreendimento, que pode conter centenas de unidades.')
    plot(cost_figure(history,period,simple),key_prefix,height=760)
    st.caption('*2026: contratações até 30/06 e IPCA médio de janeiro–junho. Anos sem registros não foram tratados como execução zero. Todas as barras usam preços de dezembro de 2025; o valor bruto é administrativo e sua decomposição é calculada, não retorno efetivamente observado.')
    st.caption('A mesma hipótese de recebimento foi aplicada a todos os anos para permitir a comparação. Isso não reconstitui as regras ou os pagamentos de cada safra. Mantém-se o recorte FAR estrito e as situações contratuais da base original, inclusive distratos; não é custo por unidade entregue.')
    st.caption('A mudança da média também reflete a composição dos empreendimentos. Não é uma medida isolada de custo de construção. O número de unidades de cada ano está no hover e no CSV.')
    st.markdown(f'**O que vem da fonte:** a [SECAP (2020, pp. 27 e 29)]({SECAP}) descreve contribuição de até 10%, mas contabiliza os aportes FAR/FDS integralmente como subsídio em sua análise econômica. A aplicação uniforme de 10% e seu desconto no tempo são exercícios próprios; não devem ser atribuídos ao relatório.')
    with st.expander('Entender a conta e conferir os quatro cenários do documento'):
        st.write('Abatimento direto: S = 0,90 × V. Valor presente: S = V − VP(recebimentos). Os 60 meses e os 6% reais são hipóteses da dissertação. Descontar as parcelas transforma a contribuição de 10% antes do desconto temporal em 8,65% do valor inicial em VP; por isso o subsídio em VP é 91,35%, não 90%. Isenções e perdas só podem reduzir os recebimentos.')
        methods=pd.DataFrame({'Leitura':['Abatimento direto de 10%, sem desconto temporal','Dissertação: 60 parcelas reais a 6% a.a.','Aportes considerados integralmente (convenção SECAP)'],
            'Subsídio por unidade (R$)':[.9*default,far_subsidy(default),default]})
        st.dataframe(methods,hide_index=True,width='stretch')
        st.caption('Comparação na referência 2024–2025. Valor contratado por unidade é uma proxy; não equivale à série de aportes orçamentários efetivos analisada pela SECAP.')
        table(reference_scenarios(default),key_prefix+'_scenarios')
    return history


def render_detail(key_prefix):
    d=summary_data()
    row=d.iloc[0]
    st.write('A Figura 1 caracteriza o subsídio registrado nas faixas da linha financiada. Esta síntese complementa a caracterização com o **subsídio líquido estimado por unidade da linha FAR**, na referência de 2024–2025.')
    plot(summary_figure(d),key_prefix,height=500)
    st.caption(f'Média ponderada por {br(row["Unidades habitacionais"],0)} unidades contratadas em 2024–2025. Valor bruto médio de R$ {br(row[GROSS],2)} menos R$ {br(row[RET],2)} de recebimentos hipotéticos em valor presente = R$ {br(row[NET],2)} de subsídio líquido por unidade.')
    st.caption('Cenário da dissertação: contribuição total de 10% em 60 parcelas reais, desconto real de 6% a.a., sem isenções ou perdas. O valor é uma estimativa sob essas hipóteses; não é média observada de subsídio efetivamente pago.')
    st.caption('Leitura conjunta: a Figura 1 usa subsídios registrados em valores correntes de 2023–2025; esta figura usa uma estimativa FAR de 2024–2025 em preços de dezembro de 2025. As medidas caracterizam apoios distintos e não representam o custo econômico integrado de todas as modalidades.')
    with st.expander('Complemento · histórico FAR e decomposição do valor por unidade',expanded=False):
        history=render_history(key_prefix+'_history')
        table(history,key_prefix+'_history')
    return d
