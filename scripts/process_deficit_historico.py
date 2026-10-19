"""Consolida totais publicados pela FJP, sem estimar anos ou alterar a base 2022.

python scripts/process_deficit_historico.py
Os XLSX originais são baixados para data/raw (ignorado pelo Git). Os números
antigos são transcrições documentadas, não reconstruções a partir de microdados.
"""
import csv
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/processed'
RAW = ROOT / 'data/raw/fjp_historico'
ACCESS = '2026-10-19'
OLD = 'https://www.unmp.org.br/wp-content/uploads/2009/06/Deficit%20Habitacional%20no%20Brasil%202007-Versao%20Final%20.pdf'
SECAP = 'https://www.gov.br/gestao/pt-br/central-de-conteudo/publicacoes/boletins/boletim-subsidios/arquivos/2019/boletim-mensal-sobre-os-subsidios-da-uniao-2013-programa-minha-casa-minha-vida-edicao-10.pdf'
REPORT_2024 = 'https://drive.google.com/file/d/1wcGG-95LHqzhjXbtTvCnFh2XX2vL0xyW/view'
BOOKS = {
    '2016_2019': '1y0c_oDcNpcq29fJyPAA4jtjDTAzij2MW',
    '2023': '1lQzsAuzhRCEJufiIEI_tVzO4vllcBT38',
    '2024': '1AwlL17JBmASv8Jurnkb6zhfXc0fzGQwp',
}


def main():
    rows, originals = [], []

    def add(year, value, series, edition, url, locator, note, percent=None):
        rows.append(dict(ano=year, territorio='Brasil', deficit_domicilios=int(round(value)),
                         percentual_domicilios=percent, serie_metodologica=series,
                         edicao_fonte=edition, fonte_url=url, localizador_fonte=locator,
                         nota=note, data_acesso=ACCESS))

    # FJP/Ministério das Cidades, relatório 2007, tabela 5.1, p. impressa 54.
    # Republicação retrospectiva; não são cinco primeiras edições originais.
    for year, value, percent in [(1991,5374380,15.4),(2000,7222645,16.1),
                                 (2004,7804619,15.1),(2005,7902699,14.9),(2006,7934719,14.5)]:
        note = 'Metodologia antiga: todas as famílias conviventes; exclui adensamento de alugados.'
        if year == 1991:
            note += ' Sem estimativas das áreas rurais da região Norte não pesquisadas pela Pnad.'
        if year == 2000:
            note += ' Inclui depreciação, não calculada nos demais anos desta tabela.'
        add(year,value,'Metodologia anterior a 2007','FJP 2007: retrospectiva publicada em 2009',
            OLD,'Tabela 5.1, p. 54 (PDF p. 54)',note,percent)

    # Série FJP reproduzida pelo Ministério da Economia/SECAP, edição 10/2019,
    # gráfico 1, p. 6 impressa (PDF p. 7). Mantém a edição desta consolidação.
    for year, value in [(2007,5855375),(2008,5437709),(2009,5897976),(2010,6940691),
                        (2011,5581968),(2012,5430562),(2013,5846040),(2014,6068061),(2015,6355743)]:
        series = 'Censo 2010' if year == 2010 else 'Pnad anual · 2007–2015'
        note = ('Censo: metodologia distinta da Pnad; não interpretar o salto como variação anual homogênea.'
                if year == 2010 else 'Quatro componentes; série FJP consolidada pela SECAP em 2019. Não concatenar como série homogênea com PnadC.')
        add(year,value,series,'SECAP 2019: série FJP consolidada',SECAP,'Gráfico 1, p. 6 (PDF p. 7)',note)

    RAW.mkdir(parents=True,exist_ok=True)
    for name, file_id in BOOKS.items():
        path = RAW / f'{name}.xlsx'
        url = f'https://docs.google.com/spreadsheets/d/{file_id}/edit'
        download = f'https://drive.google.com/uc?export=download&id={file_id}'
        if not path.exists():
            with urlopen(download,timeout=60) as response:
                content = response.read()
            if not content.startswith(b'PK'):
                raise ValueError(f'Download não é XLSX: {name}')
            path.write_bytes(content)
        originals.append(dict(arquivo=str(path.relative_to(ROOT)),url=url,download=download,
                              sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        workbook = openpyxl.load_workbook(path,data_only=True,read_only=True)
        sheet = workbook['Déficit' if name == '2016_2019' else 'Deficit_habitacional']
        for row in sheet.iter_rows(min_row=2):
            territory = row[2].value if name == '2016_2019' else row[1].value
            if str(territory).strip() != 'Brasil':
                continue
            year = int(float(row[1 if name == '2016_2019' else 0].value))
            total, percent = (row[5],row[8]) if name == '2016_2019' else (row[4],row[5])
            revised = name == '2016_2019'
            add(year,total.value,'PnadC + CadÚnico',
                'FJP: planilha reponderada 15/06/2023' if revised else f'FJP: estimativas {year}',
                url,f'{sheet.title}!{total.coordinate}; percentual: {percent.coordinate}',
                'Reponderação da PnadC; substitui a primeira publicação de 2016–2019.' if revised else
                'Tratamento de improvisados/CadÚnico revisto; consultar relatório 2024, seção 2. Variação não é efeito causal do MCMV.',
                round(float(percent.value)*100,6))
        workbook.close()

    # Somente leitura da transcrição 2022 autorizada e preservada.
    with (DATA/'deficit_fjp_faixa_componente.csv').open(encoding='utf-8') as f:
        match = [r for r in csv.DictReader(f) if r['territorio']=='Brasil'
                 and r['componente']=='deficit_total' and r['faixa']=='total']
    assert len(match)==1
    meta_2022 = json.loads((DATA/'deficit_fjp_faixa_componente.meta.json').read_text(encoding='utf-8'))
    add(2022,int(match[0]['deficit_domicilios']),'PnadC + CadÚnico','FJP 2022: transcrição preservada',
        meta_2022['bases'][0]['url'],'Tabela 4; linha Brasil/total da base fornecida',
        'Total publicado preservado; não recalculado. Improvisados utilizam informações do CadÚnico de 2021; ver relatório FJP 2024, seção 2.')
    rows.sort(key=lambda r:r['ano'])
    assert len(rows)==21 and len({r['ano'] for r in rows})==21
    assert not {2020,2021}&{r['ano'] for r in rows}
    with (DATA/'deficit_fjp_historico.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    bases=[dict(nome='FJP: catálogo de relatórios e planilhas',url='https://fjp.mg.gov.br/deficit-habitacional-no-brasil/'),
           dict(nome='FJP 2007, tabela retrospectiva 5.1 (cópia do relatório na UNMP)',url=OLD),
           dict(nome='Ministério da Economia/SECAP, Boletim de Subsídios 10/2019, gráfico 1 (fonte FJP)',url=SECAP),
           dict(nome='FJP: relatório 2024, seção 2 e tabela 1',url=REPORT_2024)]
    bases += [dict(nome=f'FJP: planilha {name}',url=f'https://docs.google.com/spreadsheets/d/{file_id}/edit')
              for name,file_id in BOOKS.items()]
    meta=dict(id='deficit_fjp_historico',titulo='Déficit habitacional nacional: publicações históricas, 1991–2024',
              organizacao='Fundação João Pinheiro; consolidação histórica SECAP',data_acesso=ACCESS,
              bases=bases,originais=originals,script='scripts/process_deficit_historico.py',
              tabela='data/processed/deficit_fjp_historico.csv',premissas=[
                  'Ano de referência da pesquisa, não ano de publicação. 21 observações; não há uma divulgação para cada ano do calendário.',
                  'Uma edição identificada por ano; não é um inventário de todas as versões e revisões de cada estimativa.',
                  '1991–2006: retrospectiva da tabela 5.1 do relatório 2007; definição antiga e diferenças de cobertura. 2000 inclui depreciação.',
                  '2007–2015: consolidação SECAP/FJP; 2010 é Censo e deve ser distinguido dos anos Pnad.',
                  'Desde 2016: PnadC + CadÚnico. 2016–2019 reponderados. Ajustes nos improvisados em 2022–2024 também afetam comparabilidade.',
                  '2020 e 2021 sem observações nesta série; não interpolar, preencher com zero ou repetir 2019.',
                  'Dados de entrada publicados, arredondados ao domicílio; não recalculamos o déficit a partir dos microdados.',
                  'Não aplicar composição de 2022 a outro total; mudanças agregadas não identificam efeito causal do MCMV.',
                  'Relatório e planilha completos de 2024 localizados em 19/10/2026; a antiga ressalva de disponibilidade apenas em notícia está superada.',
              ])
    (DATA/'deficit_fjp_historico.meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'OK: {len(rows)} anos de referência; 2022 preservado; 2020–2021 sem imputação.')


if __name__=='__main__':
    main()
