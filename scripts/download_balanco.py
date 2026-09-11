"""Baixa as três fontes oficiais para reproduzir os balanços."""
from pathlib import Path
from urllib.request import urlopen
BASE='https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/'
ROOT=Path(__file__).resolve().parents[1]/'data/raw'
ROOT.mkdir(parents=True,exist_ok=True)
for name in ['Demonstracao_Financeira_FGTS_2021.docx','Demonstracao_Financeira_FGTS_2023-v6.pdf','Demonstracao_Financeira_FGTS_2025.pdf']:
 p=ROOT/name
 if not p.exists():p.write_bytes(urlopen(BASE+name,timeout=60).read())
 print(name,p.stat().st_size)
