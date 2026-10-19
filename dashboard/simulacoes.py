"""Conditional cash-flow and housing scale scenarios for the dissertation."""
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from ui import DATA,plot,table,COLORS

def br(v):return f'{v:,.2f}'.replace(',','X').replace('.',',').replace('X','.')

def render_simulacoes():
    st.write('Testar a capacidade de manter aplicações e dimensionar o atendimento habitacional. Valores em reais de dezembro de 2025, salvo indicação em contrário.')
    st.info('Cenários condicionais com fluxos reais constantes. Não são previsões de insolvência nem estimativas de efeito causal do MCMV.')
    p=json.loads((DATA/'sim_parametros.json').read_text(encoding='utf8'))
    s=pd.read_csv(DATA/'sim_sustentabilidade.csv');t=pd.read_csv(DATA/'sim_trajetorias.csv');e=pd.read_csv(DATA/'sim_escala.csv');d=pd.read_csv(DATA/'sim_dfc_reconciliacao.csv')
    for c,label,value in zip(st.columns(3),['Caixa em 31/12/2025','Fluxo médio de manutenção','Fluxo de manutenção de 2025'],[p['caixa_inicial_bi'],s.iloc[0].fluxo_anual_bi,float(s[s.cenario=='Repetição de 2025'].iloc[0].fluxo_anual_bi)]):c.metric(label,'R$ '+br(value)+' bi')
    st.subheader('Reconciliação e escolha da referência')
    g=d[['ano','delta_real_bi','maintenance_real_bi']].rename(columns={'delta_real_bi':'Variação efetiva do caixa','maintenance_real_bi':'Fluxo de manutenção'}).melt(id_vars='ano',var_name='Medida',value_name='R$ bilhões')
    plot(px.bar(g,x='ano',y='R$ bilhões',color='Medida',barmode='group',color_discrete_sequence=COLORS),'sim_bridge')
    st.caption('O fluxo de manutenção exclui a transferência extraordinária PIS/PASEP, resgates líquidos de principal de títulos e recebimentos de investimentos permanentes. Mantém juros recebidos. A variação efetiva inclui todos os fluxos da DFC.')
    with st.expander('Memória da DFC e correção monetária'):
        table(d,'sim_dfc');st.write('Fonte: demonstrações financeiras do FGTS, Controladora, 2023 e 2025. Entradas originais em R$ milhares; saídas com sinal negativo. IPCA: índice de dezembro de 2025 dividido pela média mensal de cada ano.')
    st.subheader('Preservar o caixa ou consumir a reserva inicial?')
    selected=st.multiselect('Cenários',list(s.cenario.unique()),default=['Média 2023–2025','Repetição de 2025','Choques combinados'],key='sim_scenarios')
    h=st.select_slider('Horizonte (anos)',[5,10,15],value=10,key='sim_horizon')
    if selected:
        g=t[t.cenario.isin(selected)&(t.ano<=2025+h)]
        fig=px.line(g,x='ano',y='saldo_indicativo_bi',color='cenario',labels={'saldo_indicativo_bi':'Saldo indicativo (R$ bi)','ano':'Ano','cenario':'Cenário'},color_discrete_sequence=COLORS)
        years_plot=sorted(g.ano.unique())
        fig.update_xaxes(tickmode='array',tickvals=years_plot,ticktext=[str(y) for y in years_plot])
        fig.add_hline(y=0,line_dash='dot');plot(fig,'sim_paths')
        st.caption('Saldos negativos representam necessidade de financiamento ainda não coberta. A trajetória não pressupõe que o Fundo opere efetivamente com caixa negativo. Títulos e patrimônio não são somados ao caixa inicial.')
        view=s[(s.cenario.isin(selected))&(s.horizonte==h)]
        plot(px.bar(view,x='cenario',y='aporte_anual_preserva_caixa_bi',labels={'cenario':'Cenário','aporte_anual_preserva_caixa_bi':'Ajuste anual para preservar caixa (R$ bi)'},color='cenario',color_discrete_sequence=COLORS),'sim_support')
        table(view,'sim_results')
    else:st.info('Selecione ao menos um cenário.')
    with st.expander('Hipóteses e interpretação'):
        st.write('Média: 2023–2025 corrigidos pelo IPCA. Repetição de 2025: composição daquele ano, em preços de dezembro. Choques permanentes: −5% de depósitos, +5% de saques, −5% de recebimentos da carteira, isolados ou combinados. Expansão: +10% de novas liberações e descontos pagos. Demais fluxos constantes em termos reais.')
        st.code('Saldo = caixa inicial + horizonte × fluxo anual\nAjuste anual para preservar caixa = max(0, −fluxo anual)\nNecessidade após uso da reserva = max(0, −saldo)',language=None)
        st.write('A transferência da União é uma forma possível de ajuste, não uma despesa autorizada. O exercício abrange todo o FGTS, não apenas o MCMV. Não modela amortizações por safra, vencimentos de títulos, receitas endógenas ou novos choques. Queda de depósitos não é estimativa de pejotização.')
    st.subheader('Escala do atendimento habitacional')
    c1,c2=st.columns(2)
    year=c1.selectbox('Estoque do déficit',[2024,2022],key='sim_def_year')
    scope=c2.selectbox('Recorte',['Total','Sem ônus com aluguel'],key='sim_scope')
    c1,c2,c3=st.columns(3)
    mode=c1.selectbox('Composição',['50% FAR / 50% FGTS','100% FAR','100% FGTS Faixa 1'],key='sim_mode')
    q=c2.selectbox('Fração dos atendimentos que resolve o estoque',[1.0,.75,.5],format_func=lambda x:f'{x:.0%}',key='sim_focus')
    years=c3.selectbox('Prazo ilustrativo (anos)',[5,10,15],index=1,key='sim_years')
    r=e[(e.ano_deficit==year)&(e.recorte==scope)&(e.modalidade==mode)&(e.focalizacao==q)&(e.horizonte==years)].iloc[0]
    chart=pd.DataFrame({'Medida':['FAR: valor bruto','FGTS: crédito','Subsídio registrado'],'Estoque (R$ bi)':[r.far_bruto_bi,r.credito_fgts_bi,r.subsidio_registrado_bi],'Média anual (R$ bi)':[r.far_anual_bi,r.credito_anual_bi,r.subsidio_anual_bi]})
    plot(px.bar(chart,x='Medida',y='Média anual (R$ bi)',color='Medida',color_discrete_sequence=COLORS),'sim_scale')
    table(chart,'sim_scale_table')
    st.caption(f'Estoque: {int(r.deficit):,} domicílios; atendimentos hipotéticos: {int(round(r.atendimentos)):,}. Valores de modalidades diferentes não compõem um total de custo fiscal. A divisão pelo prazo não é um cronograma de desembolso.')
    st.write('Excluir o ônus com aluguel dimensiona um recorte, sem eliminar a necessidade de política para essas famílias. Não se estima aqui o custo de uma alternativa de locação. A composição é hipotética; não presume elegibilidade de todas as famílias ao crédito.')
    with st.expander('Parâmetros, fontes e dados completos'):
        st.write(f'FAR: R$ {br(p["far_unitario_rs"])} por unidade (registros 2024–2025). FGTS Faixa 1: principal R$ {br(p["principal_faixa1_rs"])} e subsídio registrado R$ {br(p["subsidio_faixa1_rs"])} por contrato (2023–2025). Quantidades não deflacionadas; médias ponderadas pelos contratos.')
        st.write('Déficit: FJP 2024, tabela 1; referência alternativa FJP 2022. Parâmetros: bases administrativas do Ministério das Cidades. IPCA: IBGE, SIDRA 1737. FAR 2023 ausente na extração, não interpretado como gasto zero. O subsídio registrado inclui equilíbrio e pode ter pagamento distribuído ao longo do contrato.')
        table(e,'sim_all_scale')
        st.markdown('[Memória e hipóteses no repositório](https://github.com/mestrer-a/mcmv-dashboard/blob/main/docs/simulacoes.md)')
