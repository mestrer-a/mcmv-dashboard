"""Publicações históricas FJP: anos de referência e quebras visíveis."""
import pandas as pd
import plotly.express as px
import streamlit as st

from periods import period
from ui import DATA, plot, table


def history_figure(data, ancient=False):
    d=data.copy()
    # Recent years use real numeric coordinates, including missing calendar years.
    # Numeric-looking category annotations can be interpreted as category indices
    # (e.g. 2020th category), stretching the axis and crushing all bars at the left.
    d['Ano']=d.ano.astype(str) if ancient else d.ano.astype(int)
    d['Milhões de domicílios']=d.deficit_domicilios/1e6
    d['Total publicado']=d.deficit_domicilios.map(lambda x:f'{x:,.0f}'.replace(',','.'))
    d['Rótulo']=d['Milhões de domicílios'].map(lambda x:f'{x:.2f}'.replace('.',','))
    fig=px.bar(d,x='Ano',y='Milhões de domicílios',color='serie_metodologica',text='Rótulo',
               color_discrete_map={'Pnad anual · 2007–2015':'#1f77b4','Censo 2010':'#ff7f0e',
                                   'PnadC + CadÚnico':'#26867D','Metodologia anterior a 2007':'#65778A'},
               custom_data=['Total publicado','edicao_fonte','nota'],
               labels={'serie_metodologica':'Metodologia'})
    fig.update_traces(textposition='outside',cliponaxis=False,
        hovertemplate='%{x}<br>%{customdata[0]} domicílios<br>%{customdata[1]}<extra></extra>')
    fig.update_yaxes(range=[0,d['Milhões de domicílios'].max()*1.2])
    years=(d.ano.tolist() if ancient else list(range(int(d.ano.min()),int(d.ano.max())+1)))
    if ancient:
        fig.update_xaxes(type='category',categoryorder='array',categoryarray=[str(y) for y in years],
                         tickmode='array',tickvals=[str(y) for y in years],tickangle=0)
    else:
        fig.update_traces(width=.7)
        fig.update_xaxes(type='linear',range=[years[0]-.7,years[-1]+.7],
                         tickmode='array',tickvals=years,ticktext=[str(y) for y in years],
                         tickangle=-45 if len(years)>12 else 0)
    if not ancient:
        for year in [2020,2021]:
            if year in years:
                fig.add_annotation(x=year,y=.3,text='s/d',showarrow=False,font=dict(size=13,color='#65778A'))
    return fig


def render_deficit_historico():
    st.header('Como o déficit habitacional evoluiu?')
    st.write('Totais nacionais publicados pela FJP, organizados pelo ano da pesquisa. '
             'As cores identificam metodologias diferentes; a série não é homogênea de ponta a ponta.')
    d=period(pd.read_csv(DATA/'deficit_fjp_historico.csv'),'fjp_historico',default=(1991,2024))
    if d.empty:
        return
    recent=d[d.ano>=2007]
    if not recent.empty:
        st.subheader('Déficit nacional · publicações desde 2007')
        plot(history_figure(recent),'fjp_historico_total')
        st.caption('Milhões de domicílios; valores exatos na tabela. 2010: Censo, com metodologia distinta. '
                   'A partir de 2016: Pnad Contínua + CadÚnico; 2016–2019 reponderados. '
                   '2020–2021: sem dados na série (s/d), sem interpolação. '
                   'Os ajustes de domicílios improvisados em 2022–2024 exigem cautela na leitura da queda.')
    ancient=d[d.ano<2007]
    if not ancient.empty:
        st.subheader('Publicações anteriores · referências de 1991 a 2006')
        plot(history_figure(ancient,ancient=True),'fjp_historico_antigo')
        st.caption('Observações esparsas, com espaçamento visual igual entre anos publicados. '
                   'Retrospectiva do relatório FJP 2007, tabela 5.1: a definição antiga inclui todas as famílias conviventes '
                   'e exclui adensamento de alugados. 1991 não cobre áreas rurais do Norte não pesquisadas; '
                   '2000 inclui depreciação. Não comparar diretamente com o gráfico acima.')
    table(d.rename(columns={'ano':'Ano de referência','deficit_domicilios':'Déficit (domicílios)',
                           'percentual_domicilios':'Déficit relativo (%)','fonte_url':'Fonte',
                           'localizador_fonte':'Tabela / célula','edicao_fonte':'Edição',
                           'serie_metodologica':'Metodologia','nota':'Nota'}),'fjp_historico')
    st.caption('Uma edição identificada por ano disponível, e não todas as revisões de cada publicação. '
               'Anos ausentes não são zero. Variação do déficit não mede isoladamente o impacto do MCMV. '
               'O relatório completo de 2024 já está disponível; os recortes por faixa abaixo preservam a base de 2022.')
