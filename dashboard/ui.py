"""Componentes compartilhados de leitura e interação."""
import json
from pathlib import Path
import plotly.express as px
import streamlit as st

DATA = Path(__file__).resolve().parents[1]/'data/processed'
COLORS = ['#2378A8','#DD754B','#32877A','#AD8C38','#8663A8','#65778A']

def sources(names):
    metas=[json.loads((DATA/f'{n}.meta.json').read_text(encoding='utf-8')) for n in names]
    st.caption('DADOS OFICIAIS  ·  Valores monetários correntes  ·  Acesso em 11/09/2026')
    with st.expander('Fontes, definições e premissas desta página'):
        seen=set()
        for m in metas:
            for b in m.get('bases',[]):
                if b['url'] not in seen:
                    st.markdown(f"- [{b['nome']}]({b['url']})");seen.add(b['url'])
        for m in metas:
            st.markdown('**'+m.get('titulo',m.get('id','Base'))+'**')
            for p in m.get('premissas',[]):st.write(p)

def plot(fig,key):
    fig.update_layout(template='plotly_white',height=430,margin=dict(l=15,r=15,t=65,b=20),
        font=dict(family='Arial, sans-serif',size=13,color='#25364B'),paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',hovermode='x unified',hoverdistance=-1,
        legend=dict(orientation='h',y=-.2,x=0,title_text=''),
        colorway=COLORS)
    fig.update_xaxes(showgrid=False,showspikes=True,spikemode='across',spikesnap='cursor')
    fig.update_yaxes(gridcolor='#E4EAF0',zerolinecolor='#A6B4C4')
    st.plotly_chart(fig,width='stretch',key=key,config={'displaylogo':False,'scrollZoom':False,
        'toImageButtonOptions':{'format':'png','scale':3}})

def table(df,key):
    with st.expander('Consultar valores e baixar tabela'):
        st.dataframe(df,hide_index=True,width='stretch')
        st.download_button('Baixar CSV',df.to_csv(index=False).encode('utf-8-sig'),key+'.csv',
            'text/csv',key=key+'_csv')

def line(df,x,y,color=None,labels=None):
    return px.line(df,x=x,y=y,color=color,markers=True,labels=labels,color_discrete_sequence=COLORS)
