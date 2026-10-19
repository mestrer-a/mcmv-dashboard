"""Identidades financeiras, ponderação mensal, cobertura e reconciliação das bases."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dashboard'))
from custo_oportunidade import annual_contract_rates, opportunity_estimate, comparison_figure

DATA = ROOT/'data/processed'


def main():
    # Dois meses com pesos diferentes; terceiro mês sem benchmark não entra em nenhum lado.
    m = pd.DataFrame(dict(mes=['2023-01','2023-02','2023-03'],contratos=[1,1,1],
        contratos_taxa_valida=[1,1,1],financiamento_total=[100,300,100],
        principal_taxa_valida=[100,300,100],soma_taxa_principal=[400,1800,500],
        soma_taxa_equivalente_principal=[410,1850,510]))
    b = pd.DataFrame(dict(mes=['2023-01','2023-02'],mercado_pct_aa=[10,12]))
    a = annual_contract_rates(m,b).iloc[0]
    assert np.isclose(a.contrato_pct_aa,5.5)
    assert np.isclose(a.mercado_pct_aa,11.5)  # não média simples de 11%
    assert np.isclose(a.cobertura_principal_pct,80)
    assert np.isclose(annual_contract_rates(m,b,True).iloc[0].contrato_pct_aa,5.65)
    blank = annual_contract_rates(m,b.iloc[:0]).iloc[0]
    assert pd.isna(blank.diferencial_pp) and blank.principal_comparado==0
    # Referência igual ao retorno: zero; diferença negativa preservada.
    toy = pd.DataFrame(dict(saldo_medio_rs_milhares=[1000,1000],selic_pct_ano=[5,3],receita_rs_milhares=[50,50]))
    np.testing.assert_allclose(opportunity_estimate(toy).diferencial_rs_milhares,[0,-20])
    np.testing.assert_allclose(opportunity_estimate(toy,1).diferencial_rs_milhares,[10,-10])
    fund = pd.read_csv(DATA/'custo_oportunidade_fgts.csv')
    assert list(fund.ano)==[2021,2022,2023,2024,2025]
    np.testing.assert_array_equal(fund.saldo_final_bruto_rs_milhares,
        fund.saldo_inicial_bruto_rs_milhares+fund.receita_rs_milhares+
        fund.liberacoes_liquidas_rs_milhares+fund.demais_movimentos_rs_milhares)
    np.testing.assert_array_equal(fund.saldo_inicial_bruto_rs_milhares.iloc[1:],fund.saldo_final_bruto_rs_milhares.iloc[:-1])
    # Transcrição de fonte, com a receita de 2025 identificada na Nota 9(C).
    assert fund.iloc[-1].receita_rs_milhares==36187663
    assert fund.iloc[-1].saldo_final_bruto_rs_milhares==582230648
    selic = pd.read_csv(DATA/'selic_mensal.csv')
    selic['ano'] = selic.mes.str[:4].astype(int)
    assert (selic.groupby('ano').size()==12).all()
    annual = selic.groupby('ano').selic_pct_mes.apply(lambda x:100*(np.prod(1+x/100)-1))
    np.testing.assert_allclose(fund.selic_pct_ano,annual)
    dre = pd.read_csv(DATA/'orcamento_fgts_rubrica.csv')
    expected = dre[dre.rubrica.eq('Descontos concedidos')].set_index('ano').valor_rs_milhares
    np.testing.assert_array_equal(fund.descontos_fgts_dre_rs_milhares,fund.ano.map(expected))
    monthly = pd.read_csv(DATA/'juros_contratos_mensal.csv')
    assert not monthly.duplicated(['mes','fonte','faixa_codigo']).any()
    monthly['ano'] = monthly.mes.str[:4].astype(int)
    annual_volume = monthly.groupby(['ano','fonte'])[['contratos','financiamento_total']].sum()
    existing = pd.read_csv(DATA/'exploracao_contratos.csv').groupby(['ano','fonte'])[['contratos','financiamento']].sum()
    np.testing.assert_array_equal(annual_volume.contratos,existing.contratos)
    np.testing.assert_allclose(annual_volume.financiamento_total,existing.financiamento)
    assert (monthly.contratos_taxa_valida<=monthly.contratos).all()
    market = pd.read_csv(DATA/'juros_mercado_bcb.csv')
    assert not market.mes.duplicated().any()
    if not market.empty:assert market.mes.min()=='2011-03'
    annual = annual_contract_rates(monthly,market)
    assert annual[annual.ano.lt(2011)].contrato_pct_aa.isna().all()
    assert annual[annual.ano.ge(2012)].cobertura_principal_pct.between(0,100.000001).all()
    one = fund[fund.ano.eq(2025)]
    fig = comparison_figure(one,{'retorno_contabil_bruto_pct':'Retorno'},'%')
    assert fig.layout.xaxis.range==(2024.4,2025.6)
    print('OK: ponderação, ausência de benchmark, cenários, sinais, identidade da carteira, Selic e reconciliação dos contratos.')


if __name__=='__main__':main()
