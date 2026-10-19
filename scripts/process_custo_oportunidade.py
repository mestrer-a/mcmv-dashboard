"""Transcrição auditável das DF e agregação de juros, sem alterar bases existentes.

Sem argumentos: usa caches locais do BCB (baixa se ausentes).
--skip-contracts: reconstrói apenas a carteira/BCB, sem ler os microdados.
"""
import argparse
import json
import zipfile
from pathlib import Path

import pandas as pd
import requests
from process_subsidio_medio_faixa import PROGRAMA_NORMALIZACAO, PROGRAMAS_NAO_MCMV

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/processed'
RAW = ROOT / 'data/raw'
ACCESS = '2026-10-19'
BCB_MARKET = 'https://dadosabertos.bcb.gov.br/dataset/20772-taxa-media-de-juros-das-operacoes-de-credito-com-recursos-direcionados---pessoas-fisicas---fi'
BCB_SELIC = 'https://dadosabertos.bcb.gov.br/dataset/4390-taxa-de-juros---selic-acumulada-no-mes'
DF_URL = 'https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/'

# R$ milhares; abertura, encerramento BRUTO, receita, liberações líquidas,
# demais movimentos, documento, localizador. Conferir a identidade de movimento.
# 2021: encerramento líquido 367.691.707 + provisão 529.595 = 368.221.302.
HABITACAO = [
    (2021,354970638,368221302,18256193,-4738923,-266606,
     'Demonstracao_Financeira_FGTS_2021.docx','Nota 9: movimentação; Financiamentos imobiliários'),
    (2022,368221302,394448763,24844703,1548453,-165695,
     'Demonstracao_Financeira_FGTS_2023-v6.pdf','p. 21; Nota 9(C); Habitacional'),
    (2023,394448763,445534802,26685063,26281656,-1880680,
     'Demonstracao_Financeira_FGTS_2023-v6.pdf','p. 20; Nota 9(C); Habitacional'),
    (2024,445534802,510802423,26631236,38744998,-108613,
     'Demonstracao_Financeira_FGTS_2025.pdf','p. 18; Nota 9(C); Habitacional'),
    (2025,510802423,582230648,36187663,35129497,111065,
     'Demonstracao_Financeira_FGTS_2025.pdf','p. 18; Nota 9(C); Habitacional'),
]


def sgs(code, start, end):
    path = RAW / f'bcb_sgs_{code}_{start[-4:]}_{end[-4:]}.json'
    url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados'
    if not path.exists():
        response = requests.get(url, params={'formato':'json','dataInicial':start,'dataFinal':end}, timeout=60)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list) or not data:
            raise ValueError(f'SGS {code}: resposta sem dados')
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    d = pd.DataFrame(json.loads(path.read_text(encoding='utf-8')))
    d['mes'] = pd.to_datetime(d.data, dayfirst=True).dt.strftime('%Y-%m')
    d['valor'] = pd.to_numeric(d.valor, errors='raise')
    assert not d.mes.duplicated().any()
    return d[['mes','valor']]


def metadata(name, title, bases, premises):
    meta = dict(id=name, titulo=title, data_acesso=ACCESS, bases=bases,
                script='scripts/process_custo_oportunidade.py',
                tabela=f'data/processed/{name}.csv', premissas=premises)
    (DATA/f'{name}.meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def aggregate_contracts(c):
    program = c.txt_programa_fgts.replace(PROGRAMA_NORMALIZACAO)
    c = c.loc[~program.isin(PROGRAMAS_NAO_MCMV)].copy()
    c['fonte'] = program.loc[c.index].eq('Fundo Social').map({True:'Fundo Social',False:'FGTS'})
    dates = pd.to_datetime(c.data_assinatura_financiamento, format='ISO8601', errors='raise')
    c['mes'] = dates.dt.strftime('%Y-%m')
    c['faixa_codigo'] = c.txt_compatibilidade_faixa_renda.astype('string').str.strip().fillna('Sem classificação')
    c.loc[~c.faixa_codigo.isin(['1','2','3','4']), 'faixa_codigo'] = 'Sem classificação'
    valid = c.vlr_financiamento.gt(0) & c.num_taxa_juros.between(0,100)
    c['contratos'] = 1
    c['contratos_taxa_valida'] = valid.astype(int)
    c['financiamento_total'] = c.vlr_financiamento
    c['principal_taxa_valida'] = c.vlr_financiamento.where(valid, 0)
    c['soma_taxa_principal'] = (c.num_taxa_juros*c.vlr_financiamento).where(valid, 0)
    # Converter cada taxa, antes de ponderar (não converter uma média).
    effective = 100*((1+c.num_taxa_juros/1200)**12-1)
    c['soma_taxa_equivalente_principal'] = (effective*c.vlr_financiamento).where(valid, 0)
    cols = ['contratos','contratos_taxa_valida','financiamento_total','principal_taxa_valida',
            'soma_taxa_principal','soma_taxa_equivalente_principal']
    return c.groupby(['mes','fonte','faixa_codigo'], as_index=False)[cols].sum()


def main(skip_contracts=False, market_unavailable=False):
    # Via de acesso alternativa documentada: Ipeadata republica a série do BCB.
    # Mantém a resposta original e extrai apenas os anos completos do exercício.
    ipath = RAW/'ipeadata_BM12_TJOVER12.json'
    if not ipath.exists():
        response = requests.get("https://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='BM12_TJOVER12')", timeout=45)
        response.raise_for_status()
        ipath.write_text(response.text, encoding='utf-8')
    values = pd.DataFrame(json.loads(ipath.read_text(encoding='utf-8'))['value'])
    selic = pd.DataFrame({'mes':values.VALDATA.str[:7], 'valor':pd.to_numeric(values.VALVALOR)})
    selic = selic[selic.mes.between('2021-01','2025-12')].sort_values('mes')
    selic.rename(columns={'valor':'selic_pct_mes'}).to_csv(DATA/'selic_mensal.csv', index=False)
    selic['ano'] = selic.mes.str[:4].astype(int)
    assert (selic.groupby('ano').size()==12).all(), 'A Selic exige 12 meses por ano'
    annual = selic.groupby('ano').valor.apply(lambda v:100*((1+v/100).prod()-1))
    d = pd.DataFrame(HABITACAO, columns=['ano','saldo_inicial_bruto_rs_milhares',
        'saldo_final_bruto_rs_milhares','receita_rs_milhares','liberacoes_liquidas_rs_milhares',
        'demais_movimentos_rs_milhares','arquivo_fonte','localizador_fonte'])
    assert (d.saldo_final_bruto_rs_milhares == d.saldo_inicial_bruto_rs_milhares+
            d.receita_rs_milhares+d.liberacoes_liquidas_rs_milhares+d.demais_movimentos_rs_milhares).all()
    d['saldo_medio_rs_milhares'] = (d.saldo_inicial_bruto_rs_milhares+d.saldo_final_bruto_rs_milhares)/2
    d['retorno_contabil_bruto_pct'] = 100*d.receita_rs_milhares/d.saldo_medio_rs_milhares
    d['selic_pct_ano'] = d.ano.map(annual)
    dre = pd.read_csv(DATA/'orcamento_fgts_rubrica.csv')
    discounts = dre[dre.rubrica.eq('Descontos concedidos')].set_index('ano').valor_rs_milhares
    d['descontos_fgts_dre_rs_milhares'] = d.ano.map(discounts)
    d.to_csv(DATA/'custo_oportunidade_fgts.csv', index=False)
    metadata('custo_oportunidade_fgts','Carteira habitacional: retorno e custo de oportunidade estimado',
        [{'nome':'FGTS — '+name, 'url':DF_URL+name} for name in d.arquivo_fonte.unique()]+
        [{'nome':'BCB SGS 4390 — Selic acumulada no mês', 'url':BCB_SELIC},
         {'nome':'Ipeadata — via de acesso à Selic do BCB (BM12_TJOVER12)',
          'url':"https://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='BM12_TJOVER12')"}], [
        'Carteira habitacional total do FGTS, incluindo operações antigas, FAR e dívida subordinada; não é exclusivamente MCMV.',
        '2021–2025: receita de juros/encargos/atualização monetária da Nota 9. Regime de competência, não recebimento de caixa.',
        'Saldo médio aproximado pela média da abertura e do encerramento brutos, antes de provisões. Retorno contábil bruto = receita / saldo médio.',
        'Estimativa = saldo médio × Selic anual acumulada − receita. Selic composta pelos 12 meses do SGS 4390; não é meta de dezembro.',
        'Consulta direta à API BCB indisponível em 19/10/2026. Selic obtida do Ipeadata, série BM12_TJOVER12, cuja fonte é BCB; resposta preservada em data/raw.',
        'Não deduz custos, perdas, impostos ou remuneração dos cotistas. Não é retorno líquido nem prova de insolvência. Selic é contrafactual de sensibilidade, sem equivalência de prazo, risco ou restrições legais.',
        'Descontos concedidos vêm da DRE do Fundo inteiro e são mostrados separadamente. Não somar automaticamente ao diferencial da carteira habitacional.',
        'Ajuste de cenário em pontos percentuais aplicado à Selic de cada ano; não é dado observado. Diferenças negativas são preservadas.',
        'Sem extrapolar 2020 (saldo inicial não apurado) ou 2026 (DF anual indisponível nesta base).'
    ])
    market = (pd.DataFrame(columns=['mes','mercado_pct_aa']) if market_unavailable else
              sgs(20772,'01/03/2011','31/07/2026').rename(columns={'valor':'mercado_pct_aa'}))
    market.to_csv(DATA/'juros_mercado_bcb.csv', index=False)
    if not skip_contracts:
        cols = ['data_assinatura_financiamento','txt_programa_fgts','txt_compatibilidade_faixa_renda',
                'vlr_financiamento','num_taxa_juros']
        parts = []
        with zipfile.ZipFile(RAW/'mcmv_financ_analitico_20260724.zip') as z:
            with z.open('mcmv_financ_analitico_20260724.csv') as f:
                for c in pd.read_csv(f, sep=';', decimal=',', thousands='.', usecols=cols,
                                     dtype={'txt_compatibilidade_faixa_renda':'string'}, chunksize=250000):
                    parts.append(aggregate_contracts(c))
        result = pd.concat(parts).groupby(['mes','fonte','faixa_codigo'], as_index=False).sum()
        result.to_csv(DATA/'juros_contratos_mensal.csv', index=False)
        print(f'{len(result)} agregados mensais; {result.contratos.sum():,} operações')
    metadata('juros_contratos_mensal','Juros históricos dos contratos e referência de mercado',[
        {'nome':'SNH — contratos analíticos, versão 24/07/2026',
         'url':'https://www.cidades.gov.br/images/stories/ArquivosSNH/ArquivosZIP/mcmv_financ_analitico_20260724.zip'},
        {'nome':'SNH — dicionário de dados, versão 2.4',
         'url':'https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/habitacao/arquivos-1/Dicionarios_SNH_2025_10_09.pdf'},
        {'nome':'BCB SGS 20772 — financiamento imobiliário PF, taxas de mercado', 'url':BCB_MARKET}], [
        'Mesmos filtros de programas das bases existentes: exclui Pró-Cotista e Faixa Estendida. Agregados mensais, sem publicar microdados.',
        'Taxas iniciais observadas nos contratos históricos; não são a tabela normativa de junho de 2026. 2026 parcial.',
        'Ponderação pelo principal dos contratos com financiamento positivo e taxa entre 0 e 100; cobertura exibida. Não imputar taxa ausente.',
        ('BCB 20772 indisponível na consulta de 19/10/2026: arquivo de referência contém somente cabeçalho; nenhum valor foi imputado. Dashboard exibe apenas taxas contratadas.' if market.empty else
         'BCB 20772: mensal em % a.a.; referência genérica para crédito habitacional PF de mercado, desde março de 2011. Mesmo mês e mesmos pesos da amostra MCMV.'),
        'O dicionário SNH não confirma convenção anual nominal/efetiva. Controle permite valor informado ou hipótese nominal anual capitalizada mensalmente; comparação exploratória, não harmonização comprovada.',
        'SGS reúne indexadores e perfis distintos. Não controla TR, risco, prazo, seguros ou tarifas; diferença não é CET, subsídio implícito ou receita perdida pelo FGTS.',
        'Códigos de faixa mantêm a interpretação exploratória existente, sem assumir que as regras de renda ficaram constantes.'
    ])
    print(d[['ano','retorno_contabil_bruto_pct','selic_pct_ano']].round(3).to_string(index=False))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-contracts', action='store_true')
    parser.add_argument('--market-unavailable', action='store_true', help='Explicita ausência do SGS 20772 sem imputar dados')
    args = parser.parse_args()
    main(args.skip_contracts, args.market_unavailable)
