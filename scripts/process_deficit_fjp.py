"""Total FJP 2024 divulgado pelo Ministério das Cidades na Agência Gov.
As aberturas originais FJP ainda estão pendentes; não inferir de percentuais de notícias.
"""
import csv
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'data/processed/deficit_fjp_total.csv'
URL="https://agenciagov.ebc.com.br/noticias/202604/minha-casa-minha-vida-contribui-para-o-menor-deficit-habitacional-da-historia-do-pais-afirma-ministro"
with OUT.open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['ano','territorio','deficit_domicilios','percentual_domicilios','fonte_url'])
 w.writerow([2024,'Brasil',5773983,7.4,URL])
