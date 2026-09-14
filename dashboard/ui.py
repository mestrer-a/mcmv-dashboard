"""Componentes compartilhados de leitura e interação."""
import json
from pathlib import Path
import plotly.express as px
import streamlit as st

DATA = Path(__file__).resolve().parents[1]/'data/processed'
COLORS = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#65778A']

def sources(names):
    metas=[json.loads((DATA/f'{n}.meta.json').read_text(encoding='utf-8')) for n in names]
    dates=sorted({m.get('data_acesso','não informado') for m in metas})
    st.caption('FONTES E COBERTURA  ·  Valores monetários correntes  ·  Acesso: '+', '.join(dates))
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
    fig.update_layout(template='plotly_white',height=540,margin=dict(l=30,r=35,t=65,b=80),
        font=dict(family='Arial, sans-serif',size=17,color='#25364B'),paper_bgcolor='white',
        plot_bgcolor='white',hovermode='x unified',hoverdistance=-1,
        legend=dict(orientation='h',y=-.23,x=0,title_text='',font=dict(size=16)),
        separators=',.',
        colorway=COLORS)
    fig.update_xaxes(showgrid=False,showspikes=True,spikemode='across',spikesnap='cursor',automargin=True,tickfont_size=17,title_font_size=18)
    fig.update_yaxes(gridcolor='#E4EAF0',zerolinecolor='#A6B4C4',automargin=True,tickfont_size=17,title_font_size=18)
    for trace in fig.data:
        if trace.type=='scatter':trace.update(line_width=3,marker_size=9)
    # Integer calendar years, including a visible partial-year marker.
    xs=[x for t in fig.data if t.x is not None for x in t.x]
    if xs and all(isinstance(x,(int,float)) or hasattr(x,'item') for x in xs):
        try:
            years=sorted(set(int(x) for x in xs))
            if all(2000<=x<=2100 for x in years):
                fig.update_xaxes(tickmode='array',tickvals=years,ticktext=[str(y)+('*' if y==2026 else '') for y in years])
        except (ValueError,TypeError):pass
    st.plotly_chart(fig,width='stretch',key=key,theme=None,config={'displaylogo':False,'scrollZoom':False,
        'toImageButtonOptions':{'format':'png','scale':3,'width':1400,'height':700,'filename':key}})

def table(df,key):
    with st.expander('Consultar valores e baixar tabela'):
        st.dataframe(df,hide_index=True,width='stretch')
        st.download_button('Baixar CSV',df.to_csv(index=False).encode('utf-8-sig'),key+'.csv',
            'text/csv',key=key+'_csv')

def line(df,x,y,color=None,labels=None):
    return px.line(df,x=x,y=y,color=color,markers=True,labels=labels,color_discrete_sequence=COLORS)
