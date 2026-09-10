# mcmv-dashboard

Dashboard de dados da dissertação "Custo do déficit habitacional: o desenho do
Minha Casa, Minha Vida e a sustentabilidade do FGTS" — Mestrado Profissional
em Economia e Finanças, FGV EPGE.

Cada gráfico é rastreável até o dado bruto: fonte oficial → script de
processamento → tabela tidy → gráfico (no dashboard interativo e no workbook
Excel). Ver [SOURCES.md](SOURCES.md) para as bases usadas (URL + data de
acesso) e [data_dictionary.md](data_dictionary.md) para as colunas e premissas
de limpeza aplicadas.

## Estrutura

```
data/raw/         downloads oficiais, intocados (não versionado — ver scripts/download.py)
data/processed/   tabelas tidy (CSV) + ficha de proveniência (.meta.json) por gráfico
scripts/          download.py, process_*.py, build_excel.py
dashboard/app.py  dashboard Streamlit
outputs/          graficos_reproduziveis.xlsx (aba de dados + gráfico nativo por figura)
SOURCES.md        toda base: nome, URL, data de acesso
data_dictionary.md variáveis e premissas de limpeza
```

## Reproduzir

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 scripts/download.py                          # baixa as bases oficiais (~200 MB) em data/raw/
python3 scripts/process_financiamento_fonte_ano.py    # gera data/processed/financiamento_por_fonte_ano.csv
python3 scripts/build_excel.py                        # gera outputs/graficos_reproduziveis.xlsx

streamlit run dashboard/app.py                         # dashboard interativo
```
