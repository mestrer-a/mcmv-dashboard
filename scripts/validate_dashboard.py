"""Verifica balanços, pontes, todas as leituras e recortes extremos."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dashboard'))
from juros import primeira_prestacao_sac, tabela_taxas

def main():
    taxas=tabela_taxas()
    assert taxas.shape==(8,6)
    assert taxas.iloc[:,2:].min().min()==4.00
    assert taxas.iloc[:,2:].max().max()==10.00
    assert set(taxas.Faixa)=={'Faixa 1','Faixa 2','Faixa 3','Classe Média'}
    assert list(taxas.itertuples(index=False,name=None))==[
        ('Faixa 1','Até R$ 2.160',4.00,4.25,4.50,4.75),
        ('Faixa 1','R$ 2.160,01–2.850',4.25,4.50,4.75,5.00),
        ('Faixa 1','R$ 2.850,01–3.200',4.50,4.75,5.00,5.25),
        ('Faixa 2','R$ 3.200,01–3.500',4.75,5.00,5.25,5.50),
        ('Faixa 2','R$ 3.500,01–4.000',5.50,5.50,6.00,6.00),
        ('Faixa 2','R$ 4.000,01–5.000',6.50,6.50,7.00,7.00),
        ('Faixa 3','R$ 5.000,01–9.600',7.66,7.66,8.16,8.16),
        ('Classe Média','R$ 9.600,01–13.000',10.00,10.00,10.00,10.00),
    ]
    assert np.isclose(primeira_prestacao_sac(150000,360,4.00),916.6666666666667)
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
    from periods import OPTIONS
    for page in [1,2,3,4]:
        a.sidebar.radio[0].set_value(page).run();ok()
        assert len(a.sidebar.radio)==1
        count=len(a.get('plotly_chart'))+len(a.get('vega_lite_chart'))
        assert count >= {1:15,2:12,3:5,4:5}[page],(page,count)
        if page==1:
            ids=[chart.proto.id for chart in a.get('plotly_chart')]
            assert all(any(key in chart_id for chart_id in ids) for key in
                       ['juros_faixas_2026','juros_renda_2026','juros_prestacao_2026'])
            a.selectbox(key='juros_regiao_2026').set_value('Sul, Sudeste e Centro-Oeste').run();ok()
            a.slider(key='juros_principal_2026').set_value(200000).run();ok()
        for preset in OPTIONS:
            a.radio(key='analysis_preset').set_value(preset).run();ok()
            if preset=='Personalizado':
                for yr in [2009,2022,2025,2026]:
                    a.slider(key='analysis_years').set_value((yr,yr)).run();ok()
        a.radio(key='analysis_preset').set_value(OPTIONS[0]).run();ok()
    for territory in a.selectbox[1].options:
        a.selectbox[1].set_value(territory).run();ok()
    for page in [5,0]:a.sidebar.radio[0].set_value(page).run();ok()
    print('OK: balanços e DFC reconciliados; crédito e subsídio conferidos; páginas, gráficos e anos únicos sem exceções.')

if __name__=='__main__':main()
