"""Abertura visual da dissertação, ligada às bases do dashboard."""
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from ui import DATA, plot
from revisao_objetivos import render_revisao
from far import far_subsidy, DISCOUNT_RATE
from figuras_dissertacao import render_figure, render_index, build_figure

ASSET=Path(__file__).parent/'assets/mapa_dissertacao.html'
TEAL,BLUE,GOLD='#137d81','#173e59','#c58341'

def br(value,n=2):
    return f'{value:,.{n}f}'.replace(',','X').replace('.',',').replace('X','.')

def render_inicio(navigate):
    p=json.loads((DATA/'sim_parametros.json').read_text(encoding='utf-8'))
    deficit=pd.read_csv(DATA/'deficit_fjp_total.csv')
    n=int(deficit.loc[(deficit.ano==2024)&(deficit.territorio=='Brasil'),'deficit_domicilios'].iloc[0])
    gross=p['far_unitario_rs']; net=far_subsidy(gross)
    st.caption('FGV EPGE · ARTHUR MESSER · MAPA DA DISSERTAÇÃO · REVISÃO DOS OBJETIVOS · 31/10/2026')
    st.title('Da necessidade de moradia à capacidade de financiar')
    st.write('Literatura, déficit habitacional, custo por modalidade e liquidez do FGTS: veja como cada resultado sustenta o argumento e quais hipóteses sustentam as duas respostas.')
    labels=['Déficit habitacional · 2024','FAR líquido · referência','Subsídio registrado · FGTS F1','Caixa inicial do FGTS']
    vals=[br(n/1e6)+' milhões','R$ '+br(net/1000,1)+' mil','R$ '+br(p['subsidio_faixa1_rs']/1000,1)+' mil','R$ '+br(p['caixa_inicial_bi'])+' bi']
    for col,label,value in zip(st.columns(4),labels,vals):col.metric(label,value)
    st.caption('Valores em reais de dezembro de 2025. FAR líquido é estimativa de cenário; subsídio registrado não representa todo o custo econômico da linha financiada.')
    st.button('Figura 2 · Subsídio médio por unidade FAR · 2024–2025',on_click=navigate,args=(1,'1A'),key='home_far_feature',use_container_width=True)
    render_revisao()
    tabs=st.tabs(['🧠 Mapa do argumento','📊 Evidências e resultados','🏘️ Exploração adicional FAR'])
    with tabs[0]:
        st.write('Clique nos blocos da árvore para ver sua função, fontes e fórmulas. Use o zoom e o percurso da apresentação para acompanhar as conexões.')
        html=ASSET.read_text(encoding='utf-8')
        if hasattr(st,'iframe'):st.iframe(html,height=1130)
        else:components.html(html,height=1130,scrolling=True)
        st.download_button('Baixar mapa interativo',html,'Mapa_Dissertacao.html','text/html',key='home_map_download')
    with tabs[1]:
        render_figure('1A', key_prefix='home')
        st.subheader('2 · O tamanho do problema e sua evolução')
        plot(build_figure('8'),'home_history')
        st.caption('FJP: séries separadas por metodologia. Evolução descritiva não identifica o efeito causal do MCMV.')
        st.subheader('3 · O que retorna e o que é apoio na linha financiada')
        f=go.Figure(go.Bar(x=['Principal reembolsável','Subsídio registrado'],y=[p['principal_faixa1_rs']/1000,p['subsidio_faixa1_rs']/1000],marker_color=[BLUE,GOLD],text=[br(p['principal_faixa1_rs']/1000,1),br(p['subsidio_faixa1_rs']/1000,1)],textposition='outside'))
        f.update_yaxes(title='R$ mil por contrato · Faixa 1 · 2023–2025');plot(f,'home_financed')
        st.info('O principal cria recebimentos futuros. O subsídio registrado inclui desconto e equilíbrio. A conta de referência acima acrescenta somente o benefício de juros que excede o equilíbrio registrado, sob convenção conservadora.')
        st.subheader('4 · Quando a pressão aparece no caixa do FGTS')
        plot(build_figure('13'),'home_cash')
        st.caption('Saldo anual de manutenção: insuficiência exige ajuste de fluxos ou consumo de liquidez; não indica automaticamente insolvência.')
        with st.expander('Como esses gráficos se conectam',expanded=True):
            st.write('Déficit → estoque a atender. Modalidades → forma de atendimento. Subsídio líquido → apoio por família. Caixa → recursos disponíveis em cada período. A conclusão reúne custo do estoque e capacidade de manter os desembolsos.')
    with tabs[2]:
        st.info('Exploração ilustrativa independente. Os controles abaixo não alteram a conta estática da dissertação nem sua composição histórica por faixa.')
        st.subheader('Como isenções e perdas alteram o subsídio FAR?')
        a,b,c=st.columns(3)
        e=a.slider('Famílias FAR isentas (%)',0,100,0,5,key='home_exempt')/100
        loss=b.slider('Perda dos recebimentos de pagantes (%)',0,100,0,5,key='home_loss')/100
        rate=c.number_input('Desconto nominal anual (%)',min_value=0.,max_value=30.,value=DISCOUNT_RATE*100,step=.1,format='%.4f',key='home_rate')/100
        st.caption(f'Referência: média DI até 60 meses, pregão de 29/10/2026 ({br(DISCOUNT_RATE*100,4)}% a.a.). 60 parcelas nominais fixas, sem reajuste/TR e sem carência. Não são parcelas reais constantes. A memória de cálculo e os vértices estão na Figura 2.')
        unit=far_subsidy(gross,e,loss,rate)
        st.metric('Subsídio líquido por unidade','R$ '+br(unit))
        points=pd.DataFrame({'Isenção (%)':range(0,101,5)})
        points['Subsídio por unidade (R$ mil)']=[far_subsidy(gross,x/100,loss,rate)/1000 for x in points['Isenção (%)']]
        f=px.line(points,x='Isenção (%)',y='Subsídio por unidade (R$ mil)',markers=True);f.add_vline(x=e*100,line_dash='dash',line_color=GOLD);plot(f,'home_far_sensitivity')
        st.caption('Controles são hipóteses de cenário. Perda incide somente sobre recebimentos de não isentos. O custo FAR não sai automaticamente do caixa do FGTS.')
    st.divider()
    render_index(navigate)
    st.subheader('Aprofundar cada ramo')
    for col,target,label in zip(st.columns(4),[1,4,2,6],['Programa e subsídios','Déficit habitacional','FGTS','Sustentabilidade e simulações']):col.button(label,on_click=navigate,args=(target,),key=f'home_go_{target}',use_container_width=True)
    with st.expander('Fontes e atualização da árvore'):
        st.markdown('[SECAP (2020), p. 27](https://www.gov.br/cgu/pt-br/assuntos/noticias/2021/04/cgu-divulga-prestacao-de-contas-do-presidente-da-republica-de-2020/relatorio-de-avaliacao-pmcmv.pdf) · [Ministério das Cidades: participação familiar](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/caravana-federativa/habitacao)')
        st.write('Os gráficos nativos leem as bases processadas do dashboard. O catálogo acompanha as 13 figuras de Dissertacao_Revisao_Objetivos.docx, revisão de 31/10/2026. A árvore incorpora a revisão de desconto nominal DI de 30/10/2026; a hipótese original de 6% reais permanece identificada na memória de cálculo da Figura 2. A cada nova versão da dissertação ou apresentação, conferir todos os gráficos e tabelas e avaliar mudanças no argumento, parâmetros e resultados.')
