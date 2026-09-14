"""Recortes consistentes para todas as séries; edições fixas são identificadas."""
import streamlit as st

OPTIONS = ['Recortes da dissertação', 'Governo atual · 2023–2025',
           'Governo atual · 2023–2026*', 'Série completa', 'Personalizado']

def controls(page):
    st.radio('Recorte temporal da aba', OPTIONS, horizontal=True, key='analysis_preset')
    if st.session_state.analysis_preset == 'Personalizado':
        st.slider('Intervalo personalizado',2009,2026,(2023,2025),key='analysis_years')
    st.caption('O recorte vale para todas as séries da aba. Abaixo de cada bloco é possível ajustar o período. '
               '*2026 parcial nas bases de contratos; balanços encerram em 2025. Edições fixas não são extrapoladas.')

def bounds(years, default):
    mode=st.session_state.get('analysis_preset',OPTIONS[0])
    if mode==OPTIONS[0]: return default or (min(years),max(years))
    if mode==OPTIONS[1]: return (2023,2025)
    if mode==OPTIONS[2]: return (2023,2026)
    if mode==OPTIONS[3]: return (min(years),max(years))
    return st.session_state.get('analysis_years',(2023,2025))

def period(df,key,partial=False,default=None):
    years=sorted(int(x) for x in df.ano.unique())
    if not years:return df.copy()
    if default is None:default=(2023,2025) if partial else (years[0],years[-1])
    lo,hi=bounds(years,default)
    visible=[y for y in years if lo<=y<=hi]
    if not visible:
        st.info(f'Sem observações neste recorte. Cobertura deste bloco: {years[0]}–{years[-1]}.')
        return df.iloc[:0].copy()
    # Keys include the global choice so changing it resets every local override.
    widget=f'{key}_period_{lo}_{hi}'
    if len(years)>1:
        start,end=st.select_slider('Período deste bloco',years,value=(visible[0],visible[-1]),key=widget)
    else:start=end=years[0]
    result=df[df.ano.between(start,end)].copy()
    st.caption(f'Recorte exibido: {start}–{end}'+(' · 2026 parcial' if partial and end==2026 else ''))
    return result
