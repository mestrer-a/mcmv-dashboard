"""Cenário estático autorizado: estrutura de renda 2022 aplicada aos componentes 2024."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]; D=R/'data/processed'
p=json.loads((D/'sim_parametros.json').read_text()); factors={int(k):v for k,v in p['fatores_ipca'].items()}
market=pd.DataFrame(json.loads((D/'mercado_bcb_20772_original.json').read_text()))
market['mes']=pd.to_datetime(market.data,dayfirst=True).dt.strftime('%Y-%m');market['mercado_pct_aa']=market.valor.astype(float)
market[['mes','mercado_pct_aa']].to_csv(D/'juros_mercado_bcb.csv',index=False)
a=pd.read_csv(D/'exploracao_contratos.csv');a=a[a.ano.between(2023,2025)&a.fonte.isin(['FGTS','Fundo Social'])].copy()
j=pd.read_csv(D/'juros_contratos_mensal.csv'); j=j[j.mes.str[:4].astype(int).between(2023,2025)&j.fonte.isin(['FGTS','Fundo Social'])].merge(market[['mes','mercado_pct_aa']],on='mes',validate='many_to_one')
f=pd.read_csv(D/'far_anual.csv'); f=f[f.ano.isin([2024,2025])]
f1=a[(a.faixa_codigo=='1')&a.ano.isin([2024,2025])]
share=float(f.qtd_uh.sum()/(f.qtd_uh.sum()+f1.contratos.sum()))
rub=pd.read_csv(D/'subsidio_rubricas_ano.csv',dtype={'faixa_codigo':str})
rows=[]
for faixa,g in a.groupby('faixa_codigo'):
 if faixa not in ['1','2','3','4']:continue
 n=g.contratos.sum(); fact=g.ano.map(factors)
 principal=float((g.financiamento*fact).sum()/n);explicit=float((g.subsidio_total*fact).sum()/n)
 jj=j[j.faixa_codigo==faixa];rate=float(jj.soma_taxa_principal.sum()/jj.principal_taxa_valida.sum()/100)
 mr=float((jj.mercado_pct_aa*jj.principal_taxa_valida).sum()/jj.principal_taxa_valida.sum()/100)
 # Calcula o VP dentro de cada mês/fonte antes de agregar. SAC é hipótese comum.
 rr=rub[rub.ano.between(2023,2025)&rub.faixa_codigo.eq(faixa)]
 eq=float(((rr['vlr_subsidio_equilíbrio_fgts']+rr['vlr_subsidio_equilíbrio_ogu'])*rr.ano.map(factors)).sum()/n)
 complement=explicit-eq
 def imp(months,delta=0,effective=False):
  t=np.arange(1,months+1); unit_balance=1-(t-1)/months
  value=0.
  for _,r in jj.iterrows():
   k=(1+r.mercado_pct_aa/100+delta)**(1/12)-1
   rate_m=r.soma_taxa_principal/r.principal_taxa_valida/100
   ic=(1+rate_m)**(1/12)-1 if effective else rate_m/12
   pv=float(np.sum(unit_balance*(k-ic)/(1+k)**t))
   value+=r.principal_taxa_valida*factors[int(r.mes[:4])]*pv
  return value/n
 benefit=imp(360)
 # Convenção conservadora: equilíbrio inteiramente creditado contra benefício de juros.
 # Não identifica o componente administrativo nem o custo líquido do FGTS.
 additional=max(0.,benefit-eq)
 rows.append(dict(faixa=faixa,principal=principal,explicito=explicit,equilibrio=eq,complemento=complement,taxa_contrato=rate,taxa_mercado=mr,beneficio_juros=benefit,implicito=additional,total=explicit+additional,total_sem_deducao=explicit+benefit,prazo_240=explicit+max(0,imp(240)-eq),prazo_420=explicit+max(0,imp(420)-eq),taxa_efetiva=explicit+max(0,imp(360,effective=True)-eq),taxa_menos2=explicit+max(0,imp(360,-.02)-eq),taxa_mais2=explicit+max(0,imp(360,.02)-eq),cobertura=float(jj.contratos_taxa_valida.sum()/jj.contratos.sum())))

u=pd.DataFrame(rows);u.to_csv(D/'revisao_custo_unitario.csv',index=False)
b=pd.read_csv(D/'deficit_fjp_faixa_componente.csv');b=b[(b.territorio=='Brasil')&b.faixa.ne('total')]
comp={'precaria':1156834,'coabitacao':1029372,'onus_aluguel':3587777}; allocations=[]
for c,n in comp.items():
 g=b[b.componente==c].copy();g['n_2024']=n*g.deficit_domicilios/g.deficit_domicilios.sum()
 for _,r in g.iterrows():allocations.append(dict(componente=c,faixa=r.faixa,n_2024=r.n_2024))
al=pd.DataFrame(allocations);al.to_csv(D/'revisao_deficit_alocado.csv',index=False)
v=p['far_unitario_rs'];di=pd.read_csv(D/'di_vertices_20261029.csv')
# Mesma taxa integral documentada no dashboard, sem arredondamento intermediário.
ratefar=.14530882352941177
far=v-sum(.1*v/60/(1+ratefar)**(m/12) for m in range(1,61))
results=[]
for rec in ['Total','Sem ônus de aluguel']:
 z=al if rec=='Total' else al[al.componente!='onus_aluguel']
 for faixa,n in z.groupby('faixa').n_2024.sum().items():
  code=faixa[-1] if faixa!='acima_faixa_3' else '4';r=u[u.faixa==code].iloc[0]
  far_n=n*share if code=='1' else 0;fin=n-far_n
  results.append(dict(recorte=rec,faixa=code,domicilios=n,far_unidades=far_n,financiadas=fin,far_custo=far_n*far,explicito=fin*r.explicito,implicito=fin*r.implicito,total=far_n*far+fin*r.total,total_sem_deducao=far_n*far+fin*r.total_sem_deducao,equilibrio=fin*r.equilibrio,principal=fin*r.principal))
out=pd.DataFrame(results);out.to_csv(D/'revisao_custo_deficit.csv',index=False)
summary={'far_share':share,'far_unidades_observadas':int(f.qtd_uh.sum()),'fgts_f1_observados':int(f1.contratos.sum()),'far_liquido':far,'taxa_far':ratefar,'totais':out.groupby('recorte')[['far_custo','explicito','implicito','total','total_sem_deducao','equilibrio','principal']].sum().to_dict('index'),'sustentabilidade':{'margem':p['fluxos_medios_reais_bi']['maintenance'],'queda_arrecadacao_limite_pct':100*p['fluxos_medios_reais_bi']['maintenance']/p['fluxos_medios_reais_bi']['deposits'],'retorno_cobre_credito_pct':100*p['fluxos_medios_reais_bi']['credit_receipts']/-p['fluxos_medios_reais_bi']['credit_new']}}
(D/'revisao_resultados.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
assert abs(out[out.recorte=='Total'].domicilios.sum()-5773983)<.01
assert abs(out[out.recorte!='Total'].domicilios.sum()-2186206)<.01
assert all(u.cobertura>.99)
print(u.to_string(index=False));print(json.dumps(summary,ensure_ascii=False,indent=2))
