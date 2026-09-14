"""Laboratório de pesquisa: fontes agrupadas e controles persistentes."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
st.set_page_config(page_title='MCMV · Laboratório de pesquisa',page_icon='🏘️',layout='wide')
from exploracao import render_exploracao
from ui import DATA, COLORS, sources, plot, table, line
from periods import period, controls
from additions import dissertation_charts, far_comparison, deficit_charts, budget_chart, legacy_subsidy

st.markdown("""<style>
.stApp {background:#F5F7FA;color:#25364B}
.block-container {max-width:1320px;padding-top:4rem;padding-bottom:3rem}
h1 {font-size:2.6rem!important;letter-spacing:-.04em;color:#153149}
h2,h3 {letter-spacing:-.025em}
section[data-testid="stSidebar"] {background:#EAF0F5;border-right:1px solid #D6E1EB}
div[data-testid="stMetric"] {background:white;border:1px solid #E0E7EF;padding:18px;border-radius:14px}
div[data-testid="stExpander"] {background:white;border-radius:12px}
div[data-testid="stPlotlyChart"],div[data-testid="stVegaLiteChart"] {background:white;border-radius:16px;padding:10px}
</style>""",unsafe_allow_html=True)

@st.cache_data
def read(name):return pd.read_csv(DATA/f'{name}.csv')

def br(v):return f'{v:,.2f}'.replace(',','X').replace('.',',').replace('X','.')

SOURCES={1:['financiamento_por_fonte_ano','subsidio_medio_faixa','exploracao_contratos','faixa1_modalidade','far_anual','subsidio_rubricas_ano'],
 2:['arrecadacao_saques_fgts','orcamento_fgts_rubrica','balanco_fgts','ponte_caixa_fgts','orcamento_operacional_2026'],3:['formalizacao_pnad']}

def explore(index):
    render_exploracao(index)


def stocks():
    d=period(read('balanco_fgts'),'stocks')
    if d.empty:return
    latest=d[d.ano==d.ano.max()].set_index('rubrica').valor_rs_milhares
    for col,rub in zip(st.columns(3),['Caixa e equivalentes','Patrimônio líquido','Ativo total']):
        col.metric(f'{rub} · {d.ano.max()}','R$ '+br(latest[rub]/1e6)+' bi')
    st.subheader('Quanto o Fundo tem — e de que tipo?')
    selected=st.multiselect('Saldos',['Caixa e equivalentes','Patrimônio líquido','Ativo total','TVM circulante','TVM não circulante'],default=['Caixa e equivalentes','Patrimônio líquido'])
    t=d[d.rubrica.isin(selected)].copy();t['R$ bilhões']=t.valor_rs_milhares/1e6
    if not t.empty:plot(line(t,'ano','R$ bilhões','rubrica'),'stocks')
    else:st.info('Selecione um saldo.')
    table(t,'stocks')
    st.caption('2021 e 2022 reapresentados nas DF 2023. Patrimônio não é caixa; títulos não significam disponibilidade imediata. O ativo inclui a carteira de crédito.')
    parts=['Caixa e equivalentes','TVM circulante','TVM não circulante','Financiamentos circulantes','Financiamentos não circulantes','Outros empréstimos e recebíveis','Demais ativos']
    t=d[d.rubrica.isin(parts)].copy();t['R$ bilhões']=t.valor_rs_milhares/1e6
    st.subheader('A carteira de crédito domina o ativo')
    plot(px.bar(t,x='ano',y='R$ bilhões',color='rubrica',color_discrete_sequence=COLORS),'asset');table(t,'asset')
    st.caption('Componentes exclusivos, reconciliados ao ativo total. A carteira representa recebimentos futuros, sujeitos a prazo e risco.')
    bridge=period(read('ponte_caixa_fgts'),'bridge')
    if not bridge.empty:
        years=sorted(bridge.ano.unique())
        year=st.selectbox('Ano da ponte',years,index=len(years)-1,key='bridge_year_'+str(years))
        p=bridge[bridge.ano==year]
        st.subheader('Como o caixa mudou durante o ano?')
        fig=go.Figure(go.Waterfall(x=p.rubrica,y=p.valor_rs_milhares/1e6,measure=['absolute','relative','relative','relative','total'],increasing=dict(marker_color=COLORS[2]),decreasing=dict(marker_color=COLORS[1]),totals=dict(marker_color=COLORS[0])))
        fig.update_yaxes(title='R$ bilhões');plot(fig,'bridge');table(p,'bridge')
        st.caption('Arrecadação líquida positiva pode coexistir com queda do caixa, como em 2025. Os três fluxos da DFC reconciliam os saldos; não somar novamente descontos e empréstimos aos totais.')
    with st.expander('Como usar o estoque inicial na sustentabilidade'):
        st.write('R₀ pode partir de caixa e equivalentes. Incluir títulos exige cronograma de vencimentos ou hipótese explícita de venda. Ativo e patrimônio avaliam a estrutura patrimonial, sem substituir a restrição de caixa.')
        st.code('Caixa final = caixa inicial + fluxo operacional + fluxo de investimento + fluxo de financiamento',language=None)
        st.write('Modelar arrecadação, saques, recebimentos da carteira, novas concessões, descontos pagos e despesas. Remuneração creditada nas contas não é automaticamente saída de caixa; evitar dupla contagem quando os recursos forem sacados.')

def essentials(page):
    if page==1:
        dissertation_charts()
        far_comparison()
        st.header('Histórico do programa')
        d=period(read('financiamento_por_fonte_ano'),'sources',True,default=(2009,2026))
        d['fonte']=d.fonte.replace({'OGU':'Empreendimentos subsidiados (proxy OGU)'})
        selected=st.multiselect('Fontes',sorted(d.fonte.unique()),default=sorted(d.fonte.unique()))
        d=d[d.fonte.isin(selected)];d['R$ bilhões']=d.valor_total_financiado/1e9
        st.subheader('A história do programa pelas fontes de recursos')
        if d.empty:st.info('Selecione uma fonte para preencher o gráfico abaixo.')
        fig=px.bar(d,x='ano',y='R$ bilhões',color='fonte',color_discrete_sequence=COLORS)
        fig.update_xaxes(dtick=1)
        for i,(year,label) in enumerate([(2009,'Criação'),(2011,'Fase 2'),(2016,'Fase 3'),(2020,'CVA'),(2023,'Retomada'),(2025,'Fundo Social')]):
            if d.ano.min()<=year<=d.ano.max():
                fig.add_vline(x=year,line_width=1,line_dash='dot',line_color='#8F9DAD')
                fig.add_annotation(x=year,y=1.03+(i%2)*.09,yref='paper',text=label,showarrow=False,font=dict(size=10),xanchor='right' if year==d.ano.max() else 'center')
        plot(fig,'history');table(d,'history')
        st.caption('OGU é uma proxy pelo valor de empreendimentos subsidiados, não execução orçamentária anual. Ausência de registro não comprova gasto zero. Crédito contratado não é subsídio.')
        with st.expander('Marcos históricos',expanded=True):
            st.write('2009 · criação → 2011 · fase 2 → 2016 · fase 3 → 2020–2022 · Casa Verde e Amarela → 2023 · retomada → 2025 · Fundo Social aparece no crédito da base.')
            st.caption('Contexto temporal, sem identificação causal. A EC 95 é de dezembro de 2016 e não explica isoladamente movimentos anteriores. Tetos de renda e códigos de faixa mudam no tempo.')
        legacy_subsidy()
    elif page==2:
        st.subheader('Arrecadação e saques')
        d=period(read('arrecadacao_saques_fgts'),'flow');t=d.melt(id_vars='ano',value_vars=['arrecadacao_rs_milhares','saques_rs_milhares'],var_name='Série',value_name='valor')
        t['Série']=t['Série'].map({'arrecadacao_rs_milhares':'Arrecadação','saques_rs_milhares':'Saques'});t['R$ bilhões']=t.valor/1e6
        plot(px.bar(t,x='ano',y='R$ bilhões',color='Série',barmode='group',color_discrete_map={'Arrecadação':'#4c9c70','Saques':'#df8a34'}),'flows');table(d,'flows')
        st.caption('A diferença não é lucro nem variação do caixa. Em 2020, a transferência PIS/PASEP está excluída da arrecadação apresentada.')
        d=period(read('orcamento_fgts_rubrica'),'dre');d['R$ bilhões']=d.valor_rs_milhares/1e6
        st.subheader('Despesas reconhecidas na DRE')
        st.write('Esta tabela contábil não é a distribuição do orçamento de aplicações entre habitação, saneamento e infraestrutura.')
        plot(px.bar(d,x='ano',y='R$ bilhões',color='rubrica',color_discrete_sequence=COLORS),'dre');table(d,'dre')
    else:
        st.subheader('Participação dos ocupados com carteira')
        d=period(read('formalizacao_pnad'),'employment');d['Período']=d.ano.astype(str)+'T'+d.trimestre.astype(str);d['Com carteira (%)']=d.taxa_formalizacao_fgts*100
        if d.empty:return
        plot(line(d,'Período','Com carteira (%)'),'employment');table(d,'employment')
        st.caption('Proxy de pessoas ocupadas com carteira, não vínculos ou depósitos efetivos. Não identifica pejotização nem a massa salarial sujeita ao FGTS.')

def housing():
    sources(['deficit_fjp_total','deficit_fjp_faixa_componente','exploracao_contratos'])
    controls(4)
    deficit_charts()


with st.sidebar:
    st.markdown('## MCMV / FGTS');st.caption('LABORATÓRIO DA DISSERTAÇÃO')
    page=st.radio('Navegação',range(6),format_func=lambda x:['Visão geral','Programa e subsídios','FGTS','Emprego formal','Déficit habitacional','Custos de construção'][x]);st.divider()
if page==0:
    st.caption('FGV EPGE · ARTHUR MESSER · ORIENTADOR: FERNANDO DE HOLANDA BARBOSA FILHO')
    st.title('Minha Casa Minha Vida e sustentabilidade do FGTS')
    st.write('Investigar de onde vêm os recursos, quem recebe os subsídios e quais limites condicionam a expansão do programa.')
    for c,label,value in zip(st.columns(3),['Contratações','Balanços do FGTS','Fontes principais'],['2009–2026*','2020–2025','4']):c.metric(label,value)
    st.caption('*2026 parcial. Resultados descritivos e exercícios hipotéticos são apresentados separadamente.')
    for title,text in [('Programa e subsídios','Fontes, escala, faixas e benefícios registrados.'),('FGTS','Caixa, carteira, patrimônio e os fluxos que explicam sua evolução.'),('Emprego formal','A base potencial de contribuição no mercado de trabalho.'),('Déficit habitacional','Renda, componentes e diferentes instrumentos de política habitacional.')]:
        with st.container(border=True):st.subheader(title);st.write(text)
    st.caption('Escolha uma aba à esquerda e percorra todos os gráficos rolando a página. A hipótese de restrição financeira do FGTS será testada, não presumida.')
else:
    st.title(['','Programa e subsídios','FGTS','Emprego formal','Déficit habitacional','Custos de construção'][page])
    if page in SOURCES:
        sources(SOURCES[page]);st.caption('Passe o mouse pela área das séries temporais para consultar o período. Clique na legenda para ocultar séries; use a barra do gráfico para ampliar ou exportar.')
        controls(page)
        if page==2:
            stocks()
            budget_chart()
        essentials(page)
        st.divider()
        explore(page-1)
    elif page==4:housing()
    else:st.info('Integração SINAPI/INCC pendente. Não se infere custo de construção a partir do valor de financiamento.')
