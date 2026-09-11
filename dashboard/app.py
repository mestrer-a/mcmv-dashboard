"""Laboratório de pesquisa: fontes agrupadas e controles persistentes."""
import ast
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
st.set_page_config(page_title='MCMV · Laboratório de pesquisa',page_icon='🏘️',layout='wide')
from exploracao import render_exploracao
from ui import DATA, COLORS, sources, plot, table, line

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

def period(d,key,partial=False):
    if partial and not st.sidebar.checkbox('Incluir 2026 (parcial)',key=key+'_partial'):
        d=d[d.ano!=2026]
    years=sorted(d.ano.unique())
    if len(years)>1:
        lo,hi=st.sidebar.select_slider('Período',years,value=(years[0],years[-1]),key=key+'_period')
        d=d[d.ano.between(lo,hi)]
    return d.copy()

SOURCES={1:['financiamento_por_fonte_ano','subsidio_medio_faixa','exploracao_contratos'],
 2:['arrecadacao_saques_fgts','orcamento_fgts_rubrica','balanco_fgts','ponte_caixa_fgts'],3:['formalizacao_pnad']}

def explore(index):
    tree=ast.parse((Path(__file__).parent/'exploracao.py').read_text(encoding='utf-8'))
    fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==['render_cidades','render_fgts','render_emprego'][index])
    titles=[n.args[0].value for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='show' and isinstance(n.args[0],ast.Constant)]
    st.sidebar.selectbox('Pergunta de pesquisa',titles+['Todos'],key='explore_chart')
    render_exploracao(index)

def stocks():
    d=period(read('balanco_fgts'),'stocks');latest=d[d.ano==d.ano.max()].set_index('rubrica').valor_rs_milhares
    for col,rub in zip(st.columns(3),['Caixa e equivalentes','Patrimônio líquido','Ativo total']):
        col.metric(f'{rub} · {d.ano.max()}','R$ '+br(latest[rub]/1e6)+' bi')
    topic=st.sidebar.radio('Gráfico',['Caixa e patrimônio','Composição do ativo','Ponte do caixa'],key='stocks_topic')
    if topic=='Caixa e patrimônio':
        st.subheader('Quanto o Fundo tem — e de que tipo?')
        selected=st.sidebar.multiselect('Saldos',['Caixa e equivalentes','Patrimônio líquido','Ativo total','TVM circulante','TVM não circulante'],default=['Caixa e equivalentes','Patrimônio líquido'])
        t=d[d.rubrica.isin(selected)].copy();t['R$ bilhões']=t.valor_rs_milhares/1e6
        if not t.empty:plot(line(t,'ano','R$ bilhões','rubrica'),'stocks')
        else:st.info('Selecione um saldo.')
        table(t,'stocks')
        st.caption('2021 e 2022 reapresentados nas DF 2023. Patrimônio não é caixa; títulos não significam disponibilidade imediata. O ativo inclui a carteira de crédito.')
    elif topic=='Composição do ativo':
        parts=['Caixa e equivalentes','TVM circulante','TVM não circulante','Financiamentos circulantes','Financiamentos não circulantes','Outros empréstimos e recebíveis','Demais ativos']
        t=d[d.rubrica.isin(parts)].copy();t['R$ bilhões']=t.valor_rs_milhares/1e6
        st.subheader('A carteira de crédito domina o ativo')
        plot(px.bar(t,x='ano',y='R$ bilhões',color='rubrica',color_discrete_sequence=COLORS),'asset');table(t,'asset')
        st.caption('Componentes exclusivos, reconciliados ao ativo total. A carteira representa recebimentos futuros, sujeitos a prazo e risco.')
    else:
        year=st.sidebar.selectbox('Ano da ponte',[2024,2025],index=1)
        p=read('ponte_caixa_fgts');p=p[p.ano==year]
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
        topic=st.sidebar.radio('Gráfico',['História por fonte','Subsídio por faixa'])
        if topic=='História por fonte':
            d=period(read('financiamento_por_fonte_ano'),'sources',True)
            d['fonte']=d.fonte.replace({'OGU':'Empreendimentos subsidiados (proxy OGU)'})
            selected=st.sidebar.multiselect('Fontes',sorted(d.fonte.unique()),default=sorted(d.fonte.unique()))
            d=d[d.fonte.isin(selected)];d['R$ bilhões']=d.valor_total_financiado/1e9
            st.subheader('A história do programa pelas fontes de recursos')
            if d.empty:return st.info('Selecione uma fonte.')
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
        else:
            d=read('subsidio_medio_faixa');st.subheader('Valor registrado por unidade e faixa')
            plot(px.bar(d,x='subsidio_medio_por_unidade',y='faixa',orientation='h',labels={'subsidio_medio_por_unidade':'R$ correntes por unidade','faixa':''}),'subsidy');table(d,'subsidy')
            st.caption('FAR: valor contratado por unidade. Financiadas: subsídio registrado. São conceitos distintos e médias de diferentes anos; não representam todo benefício implícito de juros.')
    elif page==2:
        topic=st.sidebar.radio('Gráfico',['Arrecadação e saques','Despesas reconhecidas'])
        if topic=='Arrecadação e saques':
            d=period(read('arrecadacao_saques_fgts'),'flow');t=d.melt(id_vars='ano',value_vars=['arrecadacao_rs_milhares','saques_rs_milhares'],var_name='Série',value_name='valor')
            t['Série']=t['Série'].map({'arrecadacao_rs_milhares':'Arrecadação','saques_rs_milhares':'Saques'});t['R$ bilhões']=t.valor/1e6
            plot(line(t,'ano','R$ bilhões','Série'),'flows');table(d,'flows')
            st.caption('A diferença não é lucro nem variação do caixa. Em 2020, a transferência PIS/PASEP está excluída da arrecadação apresentada.')
        else:
            d=period(read('orcamento_fgts_rubrica'),'dre');d['R$ bilhões']=d.valor_rs_milhares/1e6
            st.subheader('Despesas reconhecidas na DRE')
            st.write('Esta tabela contábil não é a distribuição do orçamento de aplicações entre habitação, saneamento e infraestrutura.')
            plot(px.bar(d,x='ano',y='R$ bilhões',color='rubrica',color_discrete_sequence=COLORS),'dre');table(d,'dre')
    else:
        d=period(read('formalizacao_pnad'),'employment');d['Período']=d.ano.astype(str)+'T'+d.trimestre.astype(str);d['Com carteira (%)']=d.taxa_formalizacao_fgts*100
        plot(line(d,'Período','Com carteira (%)'),'employment');table(d,'employment')
        st.caption('Proxy de pessoas ocupadas com carteira, não vínculos ou depósitos efetivos. Não identifica pejotização nem a massa salarial sujeita ao FGTS.')

def housing():
    sources(['deficit_fjp_total','exploracao_contratos'])
    total=read('deficit_fjp_total').iloc[0]
    st.metric('Domicílios em déficit · 2024',f'{int(total.deficit_domicilios):,}'.replace(',','.'))
    st.info('Referência mais recente identificada: 2024. As tabelas completas por renda e componente ainda não foram recuperadas do portal da FJP. Nenhum desdobramento foi inventado.')
    st.markdown('[Cartilha metodológica da FJP](https://drive.google.com/file/d/1ITXVvGuAs43gyQAVcwb_Z-P6XKGjtL1o/view)')
    st.write('Três componentes: habitação precária, coabitação e ônus excessivo com aluguel urbano. O último considera famílias com renda de até três salários mínimos que gastam mais de 30% com aluguel. Não acrescentar adensamento como quarta parcela independente.')
    st.subheader('Contratos e subsídios registrados se concentram nas mesmas faixas?')
    d=read('exploracao_contratos');d=d[d.ano!=2026]
    years=sorted(d.ano.unique());year=st.sidebar.selectbox('Ano dos contratos',years,index=len(years)-1)
    t=d[d.ano==year].groupby('faixa_codigo',as_index=False)[['contratos','financiamento','subsidio_total']].sum()
    t['Contratos (%)']=100*t.contratos/t.contratos.sum();t['Subsídio registrado (%)']=100*t.subsidio_total/t.subsidio_total.sum()
    m=t.melt(id_vars='faixa_codigo',value_vars=['Contratos (%)','Subsídio registrado (%)'],var_name='Medida',value_name='%')
    plot(px.bar(m,x='faixa_codigo',y='%',color='Medida',barmode='group',color_discrete_sequence=COLORS),'targeting');table(t,'targeting')
    st.caption('Somente universo financiado, sem FAR. Crédito favorecido pode existir sem subsídio explícito registrado. Contratos não informam déficit anterior da família; a figura não mede déficit eliminado. Bandas FJP e tetos MCMV não coincidem automaticamente.')

with st.sidebar:
    st.markdown('## MCMV / FGTS');st.caption('LABORATÓRIO DA DISSERTAÇÃO')
    page=st.radio('Navegação',range(6),format_func=lambda x:['Visão geral','Programa e subsídios','FGTS','Emprego formal','Déficit habitacional','Custos de construção'][x]);st.divider()
if page==0:
    st.caption('FGV EPGE · ARTHUR MESSER · ORIENTADOR: FERNANDO DE HOLANDA BARBOSA FILHO')
    st.title('Minha Casa Minha Vida e sustentabilidade do FGTS')
    st.write('Investigar de onde vêm os recursos, quem recebe os subsídios e quais limites condicionam a expansão do programa.')
    for c,label,value in zip(st.columns(3),['Contratações','Balanços do FGTS','Fontes principais'],['2009–2026*','2020–2025','3']):c.metric(label,value)
    st.caption('*2026 parcial. Resultados descritivos e exercícios hipotéticos são apresentados separadamente.')
    for title,text in [('Programa e subsídios','Fontes, escala, faixas e benefícios registrados.'),('FGTS','Caixa, carteira, patrimônio e os fluxos que explicam sua evolução.'),('Emprego formal','A base potencial de contribuição no mercado de trabalho.'),('Déficit habitacional','Renda, componentes e diferentes instrumentos de política habitacional.')]:
        with st.container(border=True):st.subheader(title);st.write(text)
    st.caption('Use a navegação e os filtros à esquerda. A hipótese de restrição financeira do FGTS será testada, não presumida.')
else:
    st.title(['','Programa e subsídios','FGTS','Emprego formal','Déficit habitacional','Custos de construção'][page])
    if page in SOURCES:
        sources(SOURCES[page]);st.caption('Passe o mouse pela área das séries temporais para consultar o período. Clique na legenda para ocultar séries; use a barra do gráfico para ampliar ou exportar.')
        modes=['Panorama','Explorações'] if page!=2 else ['Estoques e caixa','Fluxos e despesas','Explorações']
        mode=st.sidebar.radio('Leitura',modes,key=f'mode_{page}')
        if mode=='Explorações':explore(page-1)
        elif mode=='Estoques e caixa':stocks()
        else:essentials(page)
    elif page==4:housing()
    else:st.info('Integração SINAPI/INCC pendente. Não se infere custo de construção a partir do valor de financiamento.')
