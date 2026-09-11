"""Verifica balanços, pontes, todas as leituras e recortes extremos."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dashboard'))

def main():
    d=pd.read_csv(ROOT/'data/processed/balanco_fgts.csv')
    assert not d.duplicated(['ano','rubrica']).any()
    p=d.pivot(index='ano',columns='rubrica',values='valor_rs_milhares')
    assert (p['Ativo total']==p['Passivo total']+p['Patrimônio líquido']).all()
    assert (p.drop(columns=['Ativo total','Passivo total','Patrimônio líquido','Depósitos vinculados']).sum(axis=1)==p['Ativo total']).all()
    b=pd.read_csv(ROOT/'data/processed/ponte_caixa_fgts.csv').pivot(index='ano',columns='rubrica',values='valor_rs_milhares')
    assert (b['Caixa inicial']+b['Atividades operacionais']+b['Atividades de investimento']+b['Atividades de financiamento']==b['Caixa final']).all()
    assert (b['Caixa final']==p.loc[b.index,'Caixa e equivalentes']).all()
    d=pd.read_csv(ROOT/'data/processed/exploracao_contratos.csv')
    original=pd.read_csv(ROOT/'data/processed/financiamento_por_fonte_ano.csv')
    cmp=d.groupby(['ano','fonte']).financiamento.sum().to_frame().join(original[original.fonte!='OGU'].set_index(['ano','fonte']))
    assert np.allclose(cmp.financiamento,cmp.valor_total_financiado)
    assert np.allclose(d.subsidio_total,d.subsidio_fgts+d.subsidio_ogu)
    a=AppTest.from_file(str(ROOT/'dashboard/app.py'),default_timeout=40).run()
    def ok():assert not a.exception,a.exception
    ok()
    for page in [1,2,3]:
        a.sidebar.radio[0].set_value(page).run();ok()
        modes=a.radio(key=f'mode_{page}').options
        for mode in modes:
            a.radio(key=f'mode_{page}').set_value(mode).run();ok()
            if mode=='Explorações':
                for title in a.selectbox(key='explore_chart').options:
                    a.selectbox(key='explore_chart').set_value(title).run();ok()
                # Year singleton must not cause invalid scales or division errors.
                key=['contratos_periodo','fgts_periodo','pnad_periodo'][page-1]
                slider=a.select_slider(key=key)
                last=slider.options[-1]
                slider.set_value((int(last),int(last))).run();ok()
            else:
                radios=[r for r in a.sidebar.radio if r.label=='Gráfico']
                if radios:
                    for topic in radios[0].options:
                        next(r for r in a.sidebar.radio if r.label=='Gráfico').set_value(topic).run();ok()
    for page in [4,5,0]:a.sidebar.radio[0].set_value(page).run();ok()
    print('OK: balanços e DFC reconciliados; crédito e subsídio conferidos; páginas, gráficos e anos únicos sem exceções.')

if __name__=='__main__':main()
