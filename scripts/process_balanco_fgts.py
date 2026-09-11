"""Transcrição auditável do BP Controladora. Executar da raiz do repositório."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed'
BASE = 'https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/'
FILES = {2020: 'Demonstracao_Financeira_FGTS_2021.docx',
         2021: 'Demonstracao_Financeira_FGTS_2023-v6.pdf',
         2022: 'Demonstracao_Financeira_FGTS_2023-v6.pdf',
         2023: 'Demonstracao_Financeira_FGTS_2023-v6.pdf',
         2024: 'Demonstracao_Financeira_FGTS_2025.pdf',
         2025: 'Demonstracao_Financeira_FGTS_2025.pdf'}
# Caixa; TVM circulante; TVM não circulante; financiamentos circulantes;
# financiamentos não circulantes; outros recebíveis; outros ativos (residual);
# ativo; passivo; PL; depósitos vinculados. Unidade: R$ milhares.
VALUES = {
 2020: [25735856,8835744,96195932,45084460,352235494,9093925,28512654,565694065,452560025,113134040,450871389],
 # 01/01/2022 = encerramento de 2021, reapresentado nas DF 2023.
 2021: [29137964,22835792,121468869,43098124,365751372,8633990,22557653,613483764,496412193,117071571,493534632],
 2022: [25508325,26792372,128364724,42396864,392621401,8345357,24926098,648955141,533781046,115174095,530139744],
 2023: [28386508,26139151,123821774,48722933,439827567,8544761,28885332,704328026,578491844,125836182,576189085],
 2024: [36354059,25649839,120670985,49444417,502762338,8592449,27006538,770480625,651736378,118744247,643823574],
 2025: [33466156,21594006,124452347,56686126,568598317,4603220,28343048,837743220,711766538,125976682,709097614],
}
RUBRICAS = ['Caixa e equivalentes','TVM circulante','TVM não circulante',
 'Financiamentos circulantes','Financiamentos não circulantes','Outros empréstimos e recebíveis',
 'Demais ativos','Ativo total','Passivo total','Patrimônio líquido','Depósitos vinculados']

def main():
 rows=[]
 for year, values in VALUES.items():
  assert sum(values[:7]) == values[7], (year, 'composição do ativo')
  assert values[8]+values[9] == values[7], (year, 'equação patrimonial')
  for i,(rubrica,valor) in enumerate(zip(RUBRICAS,values)):
   page = '' if year==2020 else (2 if year in (2021,2022,2023) and i==9 else 1)
   rows.append(dict(ano=year,rubrica=rubrica,valor_rs_milhares=valor,arquivo_fonte=FILES[year],pagina_fonte=page,
    localizador_fonte='BP Controladora; tabelas 1 e 2' if year==2020 else 'BP Controladora',
    tratamento='residual do ativo' if i==6 else ('reapresentado' if year in (2021,2022) else 'publicado')))
 with (OUT/'balanco_fgts.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 meta=dict(id='balanco_fgts',titulo='Balanço patrimonial do FGTS',organizacao='FGTS / Caixa Econômica Federal',
  portal_catalogo='https://www.fgts.gov.br/Paginas/subpaginas/demonstracoes-financeiras.aspx',data_acesso='2026-09-11',
  bases=[dict(nome=file,url=BASE+file,sha256=hashlib.sha256((ROOT/'data/raw'/file).read_bytes()).hexdigest()) for file in sorted(set(FILES.values()))],
  por_que_essa_versao='DF 2025 para 2024–2025; DF 2023 para 2021–2023, incluindo reapresentação; versão editável oficial de 2021 para 2020, pois o link PDF redirecionava em ciclo.',
  script='scripts/process_balanco_fgts.py',tabela='data/processed/balanco_fgts.csv',metrica='Saldos em 31/12, R$ milhares correntes, Controladora.',
  premissas=[
   '2021 usa a coluna 01/01/2022 reapresentada. O PL originalmente publicado era 118.341.277 e o caixa 29.087.878; os saldos reapresentados são 117.071.571 e 29.137.964. Não confundir revisão contábil com fluxo.',
   '2020 usa documento editável oficial: o localizador é a tabela, não uma página PDF inventada. Os demais localizadores são páginas físicas do PDF, contadas a partir de 1.',
   'TVM circulante e não circulante são saldos contábeis ao custo amortizado. Não constituem automaticamente liquidez livre; vencimentos, restrições e perdas de venda precisam ser modelados.',
   'Patrimônio líquido é residual contábil; não é caixa nem verba orçamentária disponível. Ativo total inclui carteira de financiamentos.',
   'Financiamentos = setor público e privado, circulante + não circulante. Outros recebíveis ficam separados. Demais ativos é residual reconciliado.',
   'A soma de ativo e PL, ou de depósitos vinculados e passivo total, produz dupla contagem. As rubricas incluem subtotais e não devem ser somadas indiscriminadamente.'])
 (OUT/'balanco_fgts.meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 # Ponte de caixa: três fluxos mutuamente exclusivos da DFC, página 3 das DF 2025.
 bridge=[]
 for year,vals in {2024:[28386508,-43030210,19395511,31602250,36354059],2025:[36354059,-38324111,13286626,22149582,33466156]}.items():
  assert sum(vals[:4])==vals[4]
  for label,value in zip(['Caixa inicial','Atividades operacionais','Atividades de investimento','Atividades de financiamento','Caixa final'],vals):
   bridge.append(dict(ano=year,rubrica=label,valor_rs_milhares=value,arquivo_fonte=FILES[2025],pagina_fonte=3))
 with (OUT/'ponte_caixa_fgts.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(bridge[0]));w.writeheader();w.writerows(bridge)
 meta.update(id='ponte_caixa_fgts',titulo='Ponte do caixa do FGTS',tabela='data/processed/ponte_caixa_fgts.csv',metrica='Fluxos DFC Controladora e saldos de caixa, R$ milhares.',premissas=[
  'Fluxos operacionais, de investimento e de financiamento reconciliam a variação do caixa. Arrecadação menos saques é apenas parte da DFC.',
  '2024: fluxo de financiamento 31.602.250 difere em R$ 425 mil da subtração simples arrecadação–saques (31.602.675). Usar a linha DFC para reconciliar o caixa.',
  'Não somar novamente os descontos ou liberações de crédito aos totais da DFC. DRE segue competência e não deve ser somada a fluxos de caixa.'])
 (OUT/'ponte_caixa_fgts.meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('OK: 6 balanços reconciliados e 2 pontes de caixa.')

if __name__=='__main__':main()

