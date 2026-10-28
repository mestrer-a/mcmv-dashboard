# mcmv-dashboard

Dashboard de dados da dissertação "Custo do déficit habitacional: o desenho do
Minha Casa, Minha Vida e a sustentabilidade do FGTS" — Mestrado Profissional
em Economia e Finanças, FGV EPGE.

Cada gráfico é rastreável até o dado bruto: fonte oficial → script de
processamento → tabela tidy → gráfico (no dashboard interativo e no workbook
Excel). Ver [SOURCES.md](SOURCES.md) para as bases usadas (URL + data de
acesso) e [data_dictionary.md](data_dictionary.md) para as colunas e premissas
de limpeza aplicadas.

As abas Ministério das Cidades, FGTS e Emprego formal incluem **Explorações e
hipóteses**: 18 gráficos adicionais, com filtros, fontes e download das tabelas.
Veja [EXPLORACOES.md](EXPLORACOES.md) para o roteiro de análise, limitações e
reprodução. Os novos gráficos são exibidos no dashboard; o workbook original
continua cobrindo suas figuras originais.

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

### Página inicial: mapa da dissertação

A abertura reúne **Mapa do argumento**, **Evidências e resultados** e
**Simular a linha FAR**. O mapa HTML pode ser baixado para apresentação.
Os gráficos nativos leem as bases processadas do projeto. A árvore acompanha
a revisão FAR de 23/10/2026; ao receber versões posteriores, revisar suas
conexões conforme `AGENTS.md`.

O FAR de referência supõe contribuição total de 10% em 60 parcelas reais,
desconto real de 6% a.a., sem isenção ou perda. É um cenário de alta recuperação,
não uma média nacional observada das condições atuais.

Testes: `python -m unittest discover -s tests -v`.

### Gráficos da dissertação

O índice **Gráficos da dissertação** na página inicial dá acesso às 15 figuras
(1, 1A e 2–14) de `Dissertacao_FAR_Revisada.docx`, conferida em 28/10/2026.
As reproduções fixas ficam nas seções Programa e subsídios, FGTS, Déficit
habitacional e Sustentabilidade e simulações; cada uma oferece fontes,
unidades, períodos, fórmulas, hipóteses e download dos dados.

Consulte [o inventário e a conferência cruzada](docs/graficos_dissertacao.md).
A Figura 4 está sem imagem no DOCX e foi reproduzida pela legenda e pela base
citada. O custo integrado da linha financiada continua sem mensuração.
