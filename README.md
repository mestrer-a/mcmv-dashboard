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

O FAR de referência supõe contribuição total de 10% em 60 parcelas nominais
fixas, desconto nominal de 14,5309% a.a. (média exata dos 34 vértices DI até
60 meses no pregão de 29/10/2026), sem reajuste/TR, carência, isenção ou perda. É um cenário de alta recuperação,
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

A **Figura 1A** foi redesenhada: mostra quanto do valor contratado por unidade
permanece subsidiado e amplia a comparação para os anos com registros de
2009–2026, todos em preços de dezembro de 2025. Distingue abatimento direto
de 10% de recebimentos em valor presente; os quatro cenários originais estão
na memória de cálculo. A SECAP descreve participação de até 10%, mas sua
contabilização econômica considera os aportes integralmente como subsídio;
os 60 meses e o desconto de 6% são hipóteses da dissertação.

Em 29/10/2026, a Figura 1A ganhou uma síntese principal na linguagem da Figura
1: barra vertical com o subsídio líquido médio FAR de 2024–2025. O gráfico
histórico e a decomposição anteriores permanecem no complemento expansível,
com seus controles e download, sem alterar a síntese fixa.

Em 30/10/2026, a referência passou a usar uma taxa única de oportunidade DI,
com parcelas **nominais fixas**, em vez de parcelas reais constantes. Retorno
em VP: R$ 12.587,56; subsídio líquido: R$ 161.757,63 (92,78% de R$ 174.345,19).
O valor na aquisição continua normalizado em preços de dez./2025. Os quatro
cenários originais a 6% reais permanecem identificados na memória de cálculo;
o DOCX original não foi alterado. A curva congelada, os critérios de seleção
e a proveniência secundária estão em `data/processed/di_vertices_20261029.*`.
A densidade de vértices é desigual; a média atribui o mesmo peso a cada cotação.

A lógica de VP também vale para o FDS, mas sua estimativa específica está
pendente de custo por unidade e fluxos coerentes com renda, TR e isenções.
OGU é fonte orçamentária; não somar novamente os mesmos aportes FAR/FDS.
