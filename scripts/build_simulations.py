"""Reproduce dissertation scenarios. Monetary outputs: BRL December 2025.

Source inputs are versioned under data/processed; no network required.
DFC values are Controladora, BRL thousands, transcribed from official DF.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

DATA=Path(__file__).resolve().parents[1]/'data/processed'

def build():
    ipca=pd.read_csv(DATA/'sim_ipca_mensal.csv',dtype={'mes':str})
    dec=float(ipca.loc[ipca.mes=='202512','indice'].iloc[0])
    factors=ipca.assign(ano=ipca.mes.str[:4].astype(int)).groupby('ano').indice.mean().rdiv(dec)
    df=pd.read_csv(DATA/'sim_dfc_input.csv').set_index('ano')
    op=['credit_receipts','credit_new','title_op','other_loans','admin','discounts','cash_interest','other_op']
    inv=['bond_buy','bond_principal','bond_interest','permanent','other_inv']
    assert np.allclose(df[op].sum(axis=1),df.op_total,atol=.01)
    assert np.allclose(df[inv].sum(axis=1),df.inv_total,atol=.01)
    df['net_deposits']=df.deposits+df.withdrawals
    df['fin_total']=df.net_deposits-df.pis_transfer
    df['delta_cash']=df.op_total+df.inv_total+df.fin_total
    assert np.allclose(df.delta_cash,df.cash_end-df.cash_start,atol=.01)
    df['maintenance']=df.net_deposits+df.op_total+df.bond_interest+df.other_inv
    df['factor']=factors
    df['maintenance_real_bi']=df.maintenance*df.factor/1e6
    df['delta_real_bi']=df.delta_cash*df.factor/1e6
    df.to_csv(DATA/'sim_dfc_reconciliacao.csv')
    # Gross signed flows: withdrawals/new lending/discounts negative.
    real=df.drop(columns=['factor','maintenance_real_bi','delta_real_bi']).mul(factors,axis=0)/1e6
    mean=real.mean();last=real.loc[2025]
    c0=float(df.loc[2025,'cash_end']/1e6)
    scenarios=[('Média 2023–2025',mean.maintenance),('Repetição de 2025',last.maintenance),
      ('Arrecadação −5%',mean.maintenance-.05*mean.deposits),
      ('Saques +5%',mean.maintenance+.05*mean.withdrawals),
      ('Recebimentos −5%',mean.maintenance-.05*mean.credit_receipts),
      ('Choques combinados',mean.maintenance-.05*mean.deposits+.05*mean.withdrawals-.05*mean.credit_receipts),
      ('Liberações e descontos +10%',mean.maintenance+.10*(mean.credit_new+mean.discounts))]
    rows=[];paths=[]
    for name,flow in scenarios:
        for h in [5,10,15]:
            balance=c0+h*flow
            rows.append(dict(cenario=name,horizonte=h,fluxo_anual_bi=flow,saldo_indicativo_bi=balance,
                necessidade_acumulada_bi=max(0,-balance),aporte_anual_preserva_caixa_bi=max(0,-flow),
                anos_ate_limite=(c0/-flow if flow<0 else None)))
        for t in range(16):
            paths.append(dict(cenario=name,ano=2025+t,saldo_indicativo_bi=c0+t*flow))
    pd.DataFrame(rows).to_csv(DATA/'sim_sustentabilidade.csv',index=False)
    pd.DataFrame(paths).to_csv(DATA/'sim_trajetorias.csv',index=False)
    contracts=pd.read_csv(DATA/'exploracao_contratos.csv')
    f1=contracts[(contracts.fonte=='FGTS')&(contracts.faixa_codigo.astype(str)=='1')&contracts.ano.between(2023,2025)].copy()
    assert len(f1)==3 and f1.contratos.sum()>0
    principal=float((f1.financiamento*f1.ano.map(factors)).sum()/f1.contratos.sum())
    subsidy=float((f1.subsidio_total*f1.ano.map(factors)).sum()/f1.contratos.sum())
    far=pd.read_csv(DATA/'far_anual.csv');far=far[far.ano.isin([2024,2025])].copy()
    assert len(far)==2
    farunit=float((far.val_contratado_total*far.ano.map(factors)).sum()/far.qtd_uh.sum())
    params={'caixa_inicial_bi':c0,'principal_faixa1_rs':principal,'subsidio_faixa1_rs':subsidy,
      'far_unitario_rs':farunit,'contratos_faixa1_media':float(f1.contratos.mean()),
      'unidades_far_media':float(far.qtd_uh.mean()),'fatores_ipca':{str(k):v for k,v in factors.items()},
      'fluxos_medios_reais_bi':mean.to_dict()}
    (DATA/'sim_parametros.json').write_text(json.dumps(params,ensure_ascii=False,indent=2),encoding='utf8')
    rows=[]
    for year,total,struct in [(2024,5773983,2186206),(2022,6215313,2972533)]:
      for scope,n in [('Total',total),('Sem ônus com aluguel',struct)]:
       for label,a in [('100% FAR',1),('50% FAR / 50% FGTS',.5),('100% FGTS Faixa 1',0)]:
        for q in [1,.75,.5]:
         for h in [5,10,15]:
          units=n/q
          rows.append(dict(ano_deficit=year,recorte=scope,deficit=n,modalidade=label,fracao_far=a,
            focalizacao=q,horizonte=h,atendimentos=units,far_bruto_bi=units*a*farunit/1e9,
            credito_fgts_bi=units*(1-a)*principal/1e9,subsidio_registrado_bi=units*(1-a)*subsidy/1e9,
            far_anual_bi=units*a*farunit/1e9/h,credito_anual_bi=units*(1-a)*principal/1e9/h,
            subsidio_anual_bi=units*(1-a)*subsidy/1e9/h,far_unidades_ano=units*a/h,
            fgts_contratos_ano=units*(1-a)/h))
    scale=pd.DataFrame(rows)
    assert (scale.atendimentos>=scale.deficit).all()
    scale.to_csv(DATA/'sim_escala.csv',index=False)
    print(json.dumps({'parameters':{k:v for k,v in params.items() if k!='fluxos_medios_reais_bi'},
       'scenarios':dict(scenarios)},ensure_ascii=False,indent=2))

if __name__=='__main__':build()
