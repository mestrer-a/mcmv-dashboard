"""
Baixa a série trimestral de ocupados por posição/categoria de emprego
(PNAD Contínua, tabela SIDRA 4097) para data/raw/, intocada.

Fonte: IBGE, Sistema IBGE de Recuperação Automática (SIDRA).
Tabela 4097: "Pessoas de 14 anos ou mais de idade, ocupadas na semana de
referência, por posição na ocupação e categoria do emprego no trabalho
principal" — 1º trimestre 2012 a mais recente, nível Brasil.
https://sidra.ibge.gov.br/tabela/4097

Uso: python scripts/download_pnad_formalizacao.py
"""
import sys
from pathlib import Path

import requests

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Variável 4090 = "Pessoas ocupadas" (mil pessoas). Categorias da classificação
# 11913 (posição na ocupação): Total + as 6 relevantes para a taxa de
# formalização (com/sem carteira nos 3 grupos que contribuem para o FGTS
# quando com carteira: privado, doméstico, público não-estatutário).
URL = (
    "https://apisidra.ibge.gov.br/values/t/4097/n1/1/v/4090/p/all/"
    "c11913/96165,31721,31722,31723,31724,31725,31726,31727,31728,31729,31730"
)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DIR / "pnad_4097_posicao_ocupacao.json"
    if dest.exists():
        print(f"[skip] {dest.name} já existe")
        return
    print(f"[baixando] {URL}")
    r = requests.get(URL, headers={"User-Agent": USER_AGENT}, timeout=60)
    r.raise_for_status()
    dest.write_bytes(r.content)
    print(f"[ok] salvo em {dest} ({len(r.content):,} bytes)")


if __name__ == "__main__":
    sys.exit(main())
