"""Validação independente das agregações novas, sem reprocessar a transcrição FJP."""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data/processed'
def main():
    assert hashlib.sha256((D/'deficit_fjp_faixa_componente.csv').read_bytes()).hexdigest()=='63f3dd19837df0d40062eb39bc04106f41d8f9307f377cb86b1975a97c16308c'
    f=pd.read_csv(D/'deficit_fjp_faixa_componente.csv')
    assert not f.duplicated(['ano_referencia','territorio','componente','faixa']).any()
    p=f.pivot(index=['territorio','faixa'],columns='componente',values='deficit_domicilios')
    assert (p.precaria+p.coabitacao+p.onus_aluguel-p.deficit_total).abs().max()<=5
    p=f.pivot(index=['territorio','componente'],columns='faixa',values='deficit_domicilios')
    assert (p.drop(columns='total').sum(axis=1)-p.total).abs().max()<=5
    assert p.loc[('Brasil','deficit_total'),'total']==6215313
    assert p.loc[('Brasil','onus_aluguel'),'total']==3242780
    c=pd.read_csv(D/'exploracao_contratos.csv');m=pd.read_csv(D/'faixa1_modalidade.csv')
    fin=m[m.unidade=='Operações financiadas'].set_index(['ano','fonte']).volume
    expected=c[c.faixa_codigo.astype(str)=='1'].set_index(['ano','fonte']).contratos
    pd.testing.assert_series_equal(fin.sort_index(),expected.sort_index(),check_names=False)
    far=pd.read_csv(D/'far_anual.csv').set_index('ano')
    actual=m[m.unidade=='Unidades habitacionais contratadas'].set_index('ano').volume
    pd.testing.assert_series_equal(actual.sort_index(),far.qtd_uh.sort_index(),check_names=False)
    a=c[c.ano.between(2023,2025)].groupby('faixa_codigo').sum(numeric_only=True)
    assert np.isclose(a.loc['1','subsidio_total']/a.loc['1','contratos'],44045.943968)
    assert np.isclose(a.loc['2','subsidio_total']/a.loc['2','contratos'],8177.234924)
    r=pd.read_csv(D/'subsidio_rubricas_ano.csv').set_index(['ano','faixa_codigo'])
    cols=[x for x in r.columns if x.startswith('vlr_subsidio')]
    totals=c.groupby(['ano','faixa_codigo']).subsidio_total.sum()
    assert np.allclose(r[cols].sum(axis=1).sort_index(),totals.sort_index())
    assert pd.read_csv(D/'orcamento_operacional_2026.csv').valor_rs_milhares.sum()==160500000
    print('OK: FJP intacta, totais, modalidades e rubricas reconciliados.')
if __name__=='__main__':main()
