"""Resultados estáticos da revisão de 31/10/2026; mesma memória usada no Word."""
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from ui import DATA, plot, table

def write(text):
    st.markdown(text.replace("$",r"\$"))

def load_results():
    return json.loads((DATA/'revisao_resultados.json').read_text()), pd.read_csv(DATA/'revisao_custo_deficit.csv')

def cost_figure():
    _,d=load_results()
    g=d.groupby('recorte',sort=False)[['far_custo','explicito','implicito']].sum()/1e9
    g=g.rename(columns={'far_custo':'FAR líquido','explicito':'Subsídio explícito financiado','implicito':'Benefício adicional de juros'})
    f=px.bar(g.reset_index().melt(id_vars='recorte',var_name='Componente',value_name='R$ bilhões'),y='recorte',x='R$ bilhões',color='Componente',orientation='h',color_discrete_sequence=['#244d70','#3f8b8d','#d6a052'])
    f.update_layout(yaxis_title='',legend=dict(orientation='h',y=1.3),xaxis_title='R$ bilhões de dezembro de 2025',margin=dict(t=110))
    for rec,v in g.sum(axis=1).items():f.add_annotation(x=v,y=rec,text=f'{v:.1f}'.replace('.',','),showarrow=False,xshift=25)
    return f

def render_revisao():
    s,d=load_results()
    st.subheader('As duas respostas da dissertação')
    labels=['Déficit completo','Sem ônus com aluguel','Recebimentos / liberações','Margem anual de manutenção']
    values=[f"R$ {s['totais']['Total']['total']/1e9:.1f} bi",f"R$ {s['totais']['Sem ônus de aluguel']['total']/1e9:.1f} bi",'72,1%','R$ 1,46 bi']
    for col,label,v in zip(st.columns(4),labels,values):col.metric(label,v.replace('.',','))
    st.caption('Custo estático em reais de dez./2025. Referência conservadora: dedução integral do equilíbrio do benefício de juros. Não é custo fiscal observado nem principal financiado.')
    plot(cost_figure(),'revisao_custo')
    write('Faixa 1: 22,4265% FAR e 77,5735% FGTS, pela composição bruta das contratações de 2024–2025. A distribuição de renda de 2022 é aplicada separadamente a cada componente de 2024. O grupo acima da Faixa 3 usa a Faixa 4 apenas como aproximação financeira, sem comprovar elegibilidade.')
    with st.expander('Parâmetros, cálculo e sensibilidades'):
        write('Apoio financiado = explícito + máximo(0, benefício de juros − equilíbrio). O equilíbrio inclui redução de juros e administração; a base não separa as parcelas. A dedução integral evita a soma automática de benefícios sobrepostos e pode omitir apoio administrativo. SAC 360 e taxa SNH nominal anual/12 são hipóteses; o dicionário não confirma a convenção. SGS 20772: cálculo por mês e fonte, antes de agregar. Não há controle de risco, indexador, seguros ou pré-pagamentos.')
        table(pd.read_csv(DATA/'revisao_custo_unitario.csv'),'revisao_unitarios')
        table(d,'revisao_deficit')
        table(pd.read_csv(DATA/'revisao_deficit_alocado.csv'),'revisao_alocacao')
        write('Principal reembolsável: R$ 707,84 bilhões no total e R$ 310,18 bilhões sem ônus. Permanece separado do subsídio. Faixa 4 inclui Fundo Social; FAR não é debitado automaticamente do FGTS.')
    write('O FGTS depende das novas contribuições: recebe R$ 84,44 bilhões da carteira diante de R$ 117,16 bilhões de novas liberações. A margem média de R$ 1,46 bilhão desapareceria com redução de 0,71% nas contribuições, mantidos os demais fluxos. Repetir 2025 requer R$ 7,58 bilhões anuais de ajuste; nos choques combinados, R$ 21,71 bilhões. São fluxos do Fundo inteiro, não exclusivos do MCMV, e insuficiência anual não significa insolvência.')
