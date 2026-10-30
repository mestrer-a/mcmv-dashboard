"""Valor médio FAR observado e sua decomposição sob hipóteses explícitas."""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from far import far_subsidy, DISCOUNT_RATE, DISCOUNT_DATE, DI_VERTICES
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
    d['Desconto nominal anual (%)']=DISCOUNT_RATE*100
    d['Parcelas nominais fixas']=60
    d['Reajuste anual (%)']=0
    d['Pregão DI']=DISCOUNT_DATE
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


def reference_scenarios(gross,rate=.06):
    """Preserva os quatro cenários do documento na hipótese original real."""
    scenarios=[('Referência: sem isenção, sem perda',0.,0.),
        ('50% isentos; sem perda',.5,0.),('50% isentos; perda de 20%',.5,.2),('100% isentos',1.,0.)]
    return pd.DataFrame([{'Cenário':label,'Versão':'Documento original · parcelas reais constantes',
        'Desconto real anual (%)':rate*100,'Parcelas reais':60,'Isentos (%)':e*100,'Perda dos pagantes (%)':loss*100,
        'Valor bruto (R$)':gross,'Recebimentos em VP (R$)':gross-far_subsidy(gross,e,loss,rate),
        'Subsídio líquido (R$)':far_subsidy(gross,e,loss,rate)} for label,e,loss in scenarios])


def summary_data():
    gross,n=cohort(annual_history(),'2024–2025')
    net=far_subsidy(gross)
    return pd.DataFrame([{'Modalidade':'FAR','Período':'2024–2025',
        'Unidades habitacionais':n,GROSS:gross,RET:gross-net,NET:net,
        'Base de preços':'dezembro de 2025','Contribuição hipotética (%)':10,
        'Parcelas nominais fixas':60,'Desconto nominal anual (%)':DISCOUNT_RATE*100,
        'Pregão DI':DISCOUNT_DATE,'Reajuste anual (%)':0,'Primeiro recebimento (mês)':1,'Isenção (%)':0,'Perda (%)':0}])


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
    subtitle='Abatimento direto de 10%, sem desconto temporal' if simple else f'60 parcelas nominais fixas · desconto DI de {br(DISCOUNT_RATE*100,4)}% a.a. · sem isenções ou perdas'
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
        format_func=lambda x:'Abatimento direto de 10% · sem desconto temporal' if x else 'Valor presente · referência DI nominal',key=key_prefix+'_method')
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
        st.write(f'Abatimento direto: S = 0,90 × V. Valor presente: S = V − VP(recebimentos). A referência atual usa {br(DISCOUNT_RATE*100,4)}% nominais a.a. e 60 parcelas nominais fixas. O cenário original do documento permanece abaixo: parcelas reais constantes e 6% reais a.a. A mudança envolve a taxa e a hipótese de reajuste; não é uma comparação isolada de taxas. Isenções e perdas só podem reduzir os recebimentos.')
        methods=pd.DataFrame({'Leitura':['Abatimento direto de 10%, sem desconto temporal','Dissertação: 60 parcelas reais a 6% a.a.','Atualização: 60 parcelas nominais fixas, média DI','Aportes considerados integralmente (convenção SECAP)'],
            'Subsídio por unidade (R$)':[.9*default,far_subsidy(default,rate=.06),far_subsidy(default),default]})
        st.dataframe(methods,hide_index=True,width='stretch')
        st.caption('Comparação na referência 2024–2025. Valor contratado por unidade é uma proxy; não equivale à série de aportes orçamentários efetivos analisada pela SECAP.')
        table(reference_scenarios(default),key_prefix+'_scenarios')
    return history


def render_discount_method(key_prefix):
    with st.expander('Taxa de desconto · DI, TR e aplicação ao FDS e ao OGU'):
        st.write(f'Taxa única: **{br(DISCOUNT_RATE*100,4)}% nominais a.a.** Média aritmética sem ponderação dos 34 vértices DI1 publicados entre novembro/2026 e outubro/2031, no fechamento de {DISCOUNT_DATE}. A taxa exata da média é usada na conta. Não há interpolação nem casamento individual das 60 parcelas com os vencimentos.')
        st.caption('Fonte das cotações: Taxas do Tesouro, reprodução atribuída à B3, sem conferência independente do boletim B3. A quantidade de vencimentos é desigual ao longo do horizonte: a média dá o mesmo peso a cada vértice disponível, não a cada mês nem ao volume negociado. Referência congelada neste pregão, não atualização automática ou garantia de CDI futuro.')
        st.markdown('[Cotações DI1](https://taxasdotesouro.com/juros-futuros) · [Definição do contrato na B3](https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/juros/futuro-de-taxa-media-de-depositos-interfinanceiros-de-um-dia.htm)')
        st.latex(r'S=V-(1-e)(1-\lambda)\sum_{m=1}^{60}\frac{0{,}10V/60}{(1+i)^{m/12}}')
        st.write('**DI e TR têm funções diferentes.** O DI é a referência de oportunidade escolhida para este cenário. A TR pode corrigir a obrigação contratual; não determina por si só a taxa de desconto. Aqui o reajuste foi simplificado para zero. Aplicar a taxa nominal às antigas parcelas reais sem converter inflação seria inconsistente. A referência de mercado atual também não reconstitui o custo de oportunidade histórico de cada safra.')
        st.write('**FDS:** a mesma lógica de valor presente se aplica. Porém, é preciso usar seu próprio custo por unidade e seus recebimentos esperados. A IN 28 consolidada em 2026 prevê participação conforme renda, em 60 meses, correção anual pela TR e hipóteses de dispensa. Não se deve copiar o valor médio FAR ou tratar 10% do imóvel como regra atual do FDS. Estimativa específica FDS pendente: faltam nesta conta a distribuição de renda, as isenções e os fluxos de recebimento por safra.')
        st.write('**OGU:** é uma fonte orçamentária que pode abastecer diferentes modalidades e rubricas. A avaliação deve descontar os recebimentos atribuíveis a cada operação, quando houver. Transferência sem retorno tem custo igual ao aporte nesta conta simplificada. Não somar novamente como “OGU” os mesmos recursos já contados no FAR/FDS. O custo de captação do Tesouro seria outra perspectiva de avaliação, diferente da referência DI escolhida.')
        st.markdown('[FAR/FDS: Portaria 1.248 compilada, arts. 7–9](https://www.gov.br/cidades/pt-br/acesso-a-informacao/institucional/base-juridica/portarias/2026/PortariaMCID124820231.pdf) · [FDS: IN 28 consolidada, seção 9](https://www.gov.br/cidades/pt-br/acesso-a-informacao/institucional/base-juridica/instrucoes-normativas/20260203_IN28_MCMVE_consolidada1.pdf)')
        vertices=pd.DataFrame(DI_VERTICES)
        vertices['selecionado_60m']=vertices.selecionado_60m.eq('True')
        st.dataframe(vertices,hide_index=True,width='stretch')
        st.download_button('Baixar vértices DI e seleção de 60 meses',vertices.to_csv(index=False).encode('utf-8-sig'),'di_vertices_20261029.csv','text/csv',key=key_prefix+'_di_csv')
        gross,_=cohort(annual_history())
        flows=pd.DataFrame({'Mês':range(1,61)})
        flows['Parcela nominal sem reajuste (R$)']=.1*gross/60
        flows['Fator de desconto']=(1+DISCOUNT_RATE)**(-flows['Mês']/12)
        flows['Desconto nominal anual (%)']=DISCOUNT_RATE*100
        flows['Pregão DI']=DISCOUNT_DATE
        flows['Reajuste anual (%)']=0
        flows['Base monetária do valor inicial']='dezembro de 2025'
        flows['Recebimento em VP (R$)']=flows['Parcela nominal sem reajuste (R$)']*flows['Fator de desconto']
        st.caption(f'Referência sem isenções/perdas: 60 parcelas fixas de R$ {br(.1*gross/60,2)}, total nominal de R$ {br(.1*gross,2)} antes do desconto. A escala monetária é a do valor inicial normalizado em dez./2025. Não são retornos observados nem receitas das aplicações financeiras do fundo.')
        st.download_button('Baixar os 60 recebimentos do cenário FAR',flows.to_csv(index=False).encode('utf-8-sig'),'far_recebimentos_cenario.csv','text/csv',key=key_prefix+'_flows_csv')


def render_detail(key_prefix):
    d=summary_data()
    row=d.iloc[0]
    st.write('A Figura 1 caracteriza o subsídio registrado nas faixas da linha financiada. Esta síntese complementa a caracterização com o **subsídio líquido estimado por unidade da linha FAR**, na referência de 2024–2025.')
    plot(summary_figure(d),key_prefix,height=500)
    st.caption(f'Média ponderada por {br(row["Unidades habitacionais"],0)} unidades contratadas em 2024–2025. Valor bruto médio de R$ {br(row[GROSS],2)} menos R$ {br(row[RET],2)} de recebimentos hipotéticos em valor presente = R$ {br(row[NET],2)} de subsídio líquido por unidade.')
    st.caption(f'Cenário atualizado em 30/10/2026: contribuição total de 10% em 60 parcelas nominais fixas, desconto nominal de {br(DISCOUNT_RATE*100,4)}% a.a., sem reajuste, carência, isenções ou perdas. Primeiro recebimento no fim do mês 1. Estimativa de cenário, não subsídio efetivamente observado. O VP calculado na aquisição é normalizado em preços de dezembro de 2025; as parcelas futuras não mantêm poder de compra constante.')
    render_discount_method(key_prefix)
    st.caption('Leitura conjunta: a Figura 1 usa subsídios registrados em valores correntes de 2023–2025; esta figura usa uma estimativa FAR de 2024–2025 em preços de dezembro de 2025. As medidas caracterizam apoios distintos e não representam o custo econômico integrado de todas as modalidades.')
    with st.expander('Complemento · histórico FAR e decomposição do valor por unidade',expanded=False):
        history=render_history(key_prefix+'_history')
        table(history,key_prefix+'_history')
    return d
