"""Agrega as mesmas duas versões brutas; não altera nenhuma base FJP."""
import hashlib,json,zipfile
from pathlib import Path
import pandas as pd
from process_exploracao_contratos import agregar,COLS_SUB
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw';OUT=ROOT/'data/processed'
def main():
    parts=[];detail=[]
    with zipfile.ZipFile(RAW/'mcmv_financ_analitico_20260724.zip') as z:
        cols=['data_assinatura_financiamento','txt_programa_fgts','txt_compatibilidade_faixa_renda','vlr_financiamento']+COLS_SUB
        for c in pd.read_csv(z.open('mcmv_financ_analitico_20260724.csv'),sep=';',decimal=',',thousands='.',usecols=cols,dtype={'txt_compatibilidade_faixa_renda':'string'},chunksize=250000):
            a=agregar(c);parts.append(a[a.faixa_codigo=='1'][['ano','fonte','contratos']])
            # Same cleaning; retain each subsidy field separately to audit the Word definition.
            from process_subsidio_medio_faixa import PROGRAMA_NORMALIZACAO,PROGRAMAS_NAO_MCMV
            prog=c.txt_programa_fgts.replace(PROGRAMA_NORMALIZACAO);c=c[~prog.isin(PROGRAMAS_NAO_MCMV)].copy()
            c['ano']=pd.to_datetime(c.data_assinatura_financiamento,format='ISO8601').dt.year
            c['faixa_codigo']=c.txt_compatibilidade_faixa_renda.str.strip().fillna('Sem classificação')
            c.loc[~c.faixa_codigo.isin(['1','2','3','4']),'faixa_codigo']='Sem classificação'
            c.loc[~c[COLS_SUB].notna().all(axis=1),COLS_SUB]=float('nan')
            detail.append(c.groupby(['ano','faixa_codigo'])[COLS_SUB].sum())
    fin=pd.concat(parts).groupby(['ano','fonte'],as_index=False).sum()
    fin['modalidade']='Faixa 1 financiada (FGTS/FS)';fin['unidade']='Operações financiadas'
    fin=fin.rename(columns={'contratos':'volume'})
    with zipfile.ZipFile(RAW/'mcmv_subsidiado_202606302.zip') as z:
        d=pd.read_csv(z.open('mcmv_subsidiado_20260630.csv'),sep=';',decimal=',',thousands='.')
    far=d[d.txt_modalidade.eq('FAR')].copy()
    far['ano']=pd.to_datetime(far.dt_assinatura,format='%d/%m/%Y',errors='raise').dt.year
    annual=far.groupby('ano',as_index=False)[['qtd_uh','val_contratado_total']].sum()
    annual.to_csv(OUT/'far_anual.csv',index=False)
    f=annual[['ano','qtd_uh']].rename(columns={'qtd_uh':'volume'})
    f['fonte']='FAR/OGU (proxy)';f['modalidade']='Faixa 1 subsidiada (FAR, proxy por UH)';f['unidade']='Unidades habitacionais contratadas'
    result=pd.concat([fin,f],ignore_index=True).sort_values(['ano','modalidade','fonte'])
    result.to_csv(OUT/'faixa1_modalidade.csv',index=False)
    pd.concat(detail).groupby(level=[0,1]).sum().reset_index().to_csv(OUT/'subsidio_rubricas_ano.csv',index=False)
    base=json.loads((OUT/'financiamento_por_fonte_ano.meta.json').read_text(encoding='utf-8'))
    premises=['Mesmas versões: financiado 24/07/2026 e subsidiado 30/06/2026. 2026 parcial, com datas de corte diferentes.',
    'Financiado: mesma normalização e exclusão de Pró-Cotista e Faixa Estendida; código 1; data_assinatura_financiamento. FGTS e Fundo Social mantidos, quando observados.',
    'FAR: txt_modalidade exatamente FAR, sem FAR - Compra Assistida; ano de dt_assinatura (contratação, não entrega); soma de qtd_uh, sem subtrair distratadas ou filtrar situação.',
    'Operações financiadas e unidades habitacionais não são medidas idênticas nem somadas. FAR é proxy parcial da linha subsidiada da Faixa 1; não representa todas as modalidades.',
    'Caracterização do desenho híbrido, não beneficiários únicos, entrega de unidades ou déficit eliminado.',
    'far_anual: val_contratado_total / qtd_uh é valor bruto por unidade, não desconto de contrato financiado.',
    'subsidio_rubricas_ano preserva desconto e equilíbrio separadamente. Campo administrativo não identifica automaticamente todo benefício de taxa.']
    for name,title in [('faixa1_modalidade','Atendimento registrado à Faixa 1 por modalidade'),('far_anual','FAR por ano de contratação'),('subsidio_rubricas_ano','Rubricas de subsídio por ano e faixa')]:
        m=dict(base,id=name,titulo=title,tabela=f'data/processed/{name}.csv',script='scripts/process_faixa1_modalidade.py',data_acesso='2026-09-13',premissas=premises)
        m['sha256_brutos']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [RAW/'mcmv_financ_analitico_20260724.zip',RAW/'mcmv_subsidiado_202606302.zip']}
        (OUT/f'{name}.meta.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(result[result.ano>=2023].to_string(index=False))
if __name__=='__main__':main()
