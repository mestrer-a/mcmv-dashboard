# Gráficos da dissertação — conferência de 28/10/2026

Documento: `Dissertacao_FAR_Revisada.docx`. SHA-256: `d5146be5370262388d2e1aadae895928dab8187a8d2ad3d7510c375f55dc0aee`.

Foram conferidos a lista de figuras, as legendas no corpo, as notas de fonte e as imagens embutidas: **15 figuras (1, 1A e 2–14), 14 imagens**. Não há outra figura gráfica no DOCX. A Figura 4 possui legenda, fonte e discussão, mas não imagem embutida. Sua reprodução usa o valor médio por ano/faixa da base citada; a equivalência visual com uma imagem ausente não pode ser verificada. Não há figura pendente de reprodução ou dado imputado para completar uma figura. O custo econômico integrado da linha financiada continua pendente de mensuração, como no documento.

O inventário de legendas e fontes extraídas está em `inventario_figuras.json`. A reprodução usa `dashboard/figuras_dissertacao.py`, com recortes fixos e sem depender dos controles exploratórios. O índice **Gráficos da dissertação** na abertura abre cada figura diretamente em sua seção. Na seção, o seletor **Figura do documento** permite percorrer as demais. Todas têm fonte, período, unidade, fórmula, hipóteses, tabela e download CSV. As páginas e controles anteriores permanecem disponíveis abaixo.

## Inventário e localização

| Figura | Título | Seção / acesso | Situação anterior |
|---|---|---|---|
| 1 | Subsídio registrado por contrato financiado e por faixa, 2023–2025 | Programa e subsídios → Figura 1 | Já existia: Programa e subsídios, doc_subsidy. |
| 1A | Subsídio líquido FAR: referência e sensibilidade | Programa e subsídios → Figura 1A (também na abertura → Evidências e resultados) | Ausente; fornecida no patch, incompatível textualmente com inicio.py atual. |
| 2 | Intervalos das taxas nominais da linha financiada em 2026 | Programa e subsídios → Figura 2 | Já havia mínimos/máximos em barras, juros_faixas_2026; agora também intervalos como no documento. |
| 3 | Número de operações da linha financiada (FGTS e Fundo Social) por faixa, 2023–2026 | Programa e subsídios → Figura 3 | Já existia: Programa e subsídios, doc_profile; legenda antiga dizia Figura 2. |
| 4 | Valor médio dos contratos por faixa, 2023–2026 | Programa e subsídios → Figura 4 | Já existia: Programa e subsídios, doc_ticket; legenda antiga dizia Figura 3. Imagem ausente no DOCX. |
| 5 | Financiamento do MCMV por fonte e por ano com as mudanças do Programa, 2009–2026 | Programa e subsídios → Figura 5 | Já existia: Programa e subsídios, history. |
| 6 | Arrecadação e saques em depósitos vinculados do FGTS, 2020–2025 | FGTS → Figura 6 | Já existia: FGTS, flows. |
| 7 | Caixa e patrimônio líquido do FGTS, 2020–2025 | FGTS → Figura 7 | Já existia: FGTS, stocks. |
| 8 | Déficit habitacional nacional e mudanças de base estatística | Déficit habitacional → Figura 8 | Existia histórico em barras em Déficit habitacional e linha resumida na abertura. Faltava a reprodução com pontos isolados de 2022–2024. |
| 9 | Composição do déficit habitacional em 2022 e 2024 | Déficit habitacional → Figura 9 | Ausente: havia somente componentes de 2022 por faixa; faltava a comparação nacional 2022/2024. |
| 10 | Retorno da carteira habitacional e diferencial bruto frente à Selic | FGTS → Figura 10 | Existiam painéis separados e com ajuste da Selic, opportunity_fund_rates/cost. Faltava a figura fixa de dois painéis com diferencial bruto isolado. |
| 11 | Variação efetiva do caixa e fluxo de manutenção | Sustentabilidade e simulações → Figura 11 | Já existia: Sustentabilidade e simulações, sim_bridge. |
| 12 | Saldos indicativos sob fluxos reais constantes | Sustentabilidade e simulações → Figura 12 | Existia sim_paths; padrão mostrava três cenários e dez anos. Faltava a reprodução fixa dos sete cenários até 2040. |
| 13 | Ajuste anual necessário para preservar o caixa real | Sustentabilidade e simulações → Figura 13 | Existia sim_support, dependente dos cenários selecionados; faltava a comparação fixa dos sete. |
| 14 | Escala anual média no horizonte de dez anos | Sustentabilidade e simulações → Figura 14 | Existia sim_scale para um recorte selecionado; faltava a comparação simultânea dos dois recortes em dez anos. |

## Dados, construção e hipóteses por figura

### Figura 1 — Subsídio registrado por contrato financiado e por faixa, 2023–2025

- **Período:** 2023–2025, anos completos.
- **Unidade:** R$ correntes por contrato.
- **Natureza:** Dados observados · agregação administrativa.
- **Base local:** `data/processed/exploracao_contratos.csv`.
- **Construção:** Σ(desconto FGTS + equilíbrio FGTS + desconto OGU + equilíbrio OGU) / contratos com as quatro rubricas preenchidas, incluindo zeros.
- **Hipóteses e limites:** FGTS e Fundo Social; exclui FAR. Zero registrado não exclui benefício de juros. Não é custo econômico completo.
- **Fonte:** [MCMV Financiado com FGTS/FS — dados analíticos](https://www.cidades.gov.br/images/stories/ArquivosSNH/ArquivosZIP/mcmv_financ_analitico_20260724.zip).

### Figura 1A — Subsídio líquido FAR: referência e sensibilidade

- **Período:** Contratações FAR 2024–2025; recebimentos hipotéticos nos meses 1–60.
- **Unidade:** R$ mil de dezembro de 2025 por unidade.
- **Natureza:** Cenários calculados.
- **Base local:** `data/processed/far_anual.csv`, `data/processed/sim_parametros.json`.
- **Construção:** S = V − (1−e)(1−λ) × Σ[m=1…60] (0,10V/60)/(1+0,06)^(m/12).
- **Hipóteses e limites:** V = R$ 174.345,19; contribuição histórica de 10% (SECAP 2020, p. 27), 60 parcelas reais, desconto real de 6% a.a. Cenários fixos: e=0/λ=0; e=50%/λ=0; e=50%/λ=20%; e=100%/λ=0. Isenções e perdas são hipóteses, não médias nacionais. Perda somente sobre recebimentos dos pagantes, uma única vez.
- **Fonte:** [MCMV Financiado com FGTS/FS — dados analíticos](https://www.cidades.gov.br/images/stories/ArquivosSNH/ArquivosZIP/mcmv_financ_analitico_20260724.zip); [MCMV Subsidiado — Empreendimentos](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/habitacao/programa-minha-casa-minha-vida/arquivos/mcmv_subsidiado_202606302.zip); [SECAP (2020), p. 27 · contribuição histórica de 10%](https://www.gov.br/cgu/pt-br/assuntos/noticias/2021/04/cgu-divulga-prestacao-de-contas-do-presidente-da-republica-de-2020/relatorio-de-avaliacao-pmcmv.pdf).

### Figura 2 — Intervalos das taxas nominais da linha financiada em 2026

- **Período:** Tabela de 2026; consulta do documento: 19/10/2026.
- **Unidade:** % nominal ao ano.
- **Natureza:** Regras normativas · não são médias de contratos.
- **Base local:** `dashboard/juros.py::tabela_taxas`.
- **Construção:** Mínimo e máximo das células de renda, região e condição de cotista em cada faixa.
- **Hipóteses e limites:** Faixa 1: 4–5,25%; Faixa 2: 4,75–7%; Faixa 3: 7,66–8,16%; Classe Média: 10%. Não inclui TR, seguros e tarifas; não é CET ou retorno líquido do FGTS. Não aplicar retroativamente.
- **Fonte:** [Ministério das Cidades · tabela normativa de 2026](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/habitacao/programa-minha-casa-minha-vida/mcmv-fgts).

### Figura 3 — Número de operações da linha financiada (FGTS e Fundo Social) por faixa, 2023–2026

- **Período:** 2023–2026; 2026 parcial até 24/07.
- **Unidade:** Mil operações financiadas.
- **Natureza:** Dados observados · agregação administrativa.
- **Base local:** `data/processed/exploracao_contratos.csv`.
- **Construção:** Contagem de operações por ano e código de faixa / 1.000.
- **Hipóteses e limites:** FGTS e Fundo Social; exclui OGU/FAR/FDS. Operações não são famílias únicas ou entregas. Os tetos de renda e a interpretação dos códigos mudam ao longo do tempo.
- **Fonte:** [MCMV Financiado com FGTS/FS — dados analíticos](https://www.cidades.gov.br/images/stories/ArquivosSNH/ArquivosZIP/mcmv_financ_analitico_20260724.zip).

### Figura 4 — Valor médio dos contratos por faixa, 2023–2026

- **Período:** 2023–2026; 2026 parcial até 24/07.
- **Unidade:** R$ mil correntes por operação.
- **Natureza:** Dados observados · média ponderada.
- **Base local:** `data/processed/exploracao_contratos.csv`.
- **Construção:** Soma do valor financiado / operações com valor de financiamento observado / 1.000, por ano e faixa.
- **Hipóteses e limites:** Mesmo universo da Figura 3. Principal reembolsável, não subsídio nem preço do imóvel. O DOCX contém legenda e fonte, mas não imagem para esta figura; reprodução pela definição e base citadas.
- **Fonte:** [MCMV Financiado com FGTS/FS — dados analíticos](https://www.cidades.gov.br/images/stories/ArquivosSNH/ArquivosZIP/mcmv_financ_analitico_20260724.zip).

### Figura 5 — Financiamento do MCMV por fonte e por ano com as mudanças do Programa, 2009–2026

- **Período:** 2009–2026; 2026 parcial (financiada 24/07; subsidiada 30/06).
- **Unidade:** R$ bilhões correntes contratados.
- **Natureza:** Dados observados · OGU aproximado por empreendimentos.
- **Base local:** `data/processed/financiamento_por_fonte_ano.csv`.
- **Construção:** Soma dos valores de contratação por ano e fonte / 10⁹.
- **Hipóteses e limites:** OGU é proxy de empreendimentos subsidiados, não execução orçamentária. Ausência não comprova gasto zero. Crédito contratado não é subsídio. Marcos históricos não identificam causalidade.
- **Fonte:** [MCMV Financiado com FGTS/FS — dados analíticos](https://www.cidades.gov.br/images/stories/ArquivosSNH/ArquivosZIP/mcmv_financ_analitico_20260724.zip); [MCMV Subsidiado — Empreendimentos](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/habitacao/programa-minha-casa-minha-vida/arquivos/mcmv_subsidiado_202606302.zip).

### Figura 6 — Arrecadação e saques em depósitos vinculados do FGTS, 2020–2025

- **Período:** 2020–2025.
- **Unidade:** R$ bilhões correntes.
- **Natureza:** Dados observados · DFC Controladora.
- **Base local:** `data/processed/arrecadacao_saques_fgts.csv`.
- **Construção:** Valores da DFC em R$ milhares / 10⁶.
- **Hipóteses e limites:** Arrecadação de 2020 exclui transferência extraordinária PIS/PASEP. Arrecadação menos saques não é lucro nem variação total do caixa.
- **Fonte:** [Demonstração Financeira FGTS 2025 (dá 2025 e 2024)](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2025.pdf); [Demonstração Financeira FGTS 2023-v6 (dá 2023 e 2022)](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2023-v6.pdf); [Demonstração Financeira FGTS 2021 (dá 2021 e 2020)](https://www.caixa.gov.br/Downloads/fgts-demonstracao-financeira/DEMONSTRACAO_FINANCEIRA_FGTS_2021.pdf).

### Figura 7 — Caixa e patrimônio líquido do FGTS, 2020–2025

- **Período:** Saldos de encerramento de 2020–2025.
- **Unidade:** R$ bilhões correntes.
- **Natureza:** Dados observados · Balanço Controladora.
- **Base local:** `data/processed/balanco_fgts.csv`.
- **Construção:** Caixa e equivalentes e patrimônio líquido em R$ milhares / 10⁶.
- **Hipóteses e limites:** 2021–2022 reapresentados nas DF 2023. Patrimônio líquido não é disponibilidade de caixa; não somar os estoques como capacidade de financiamento.
- **Fonte:** [Demonstracao_Financeira_FGTS_2021.docx](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2021.docx); [Demonstracao_Financeira_FGTS_2023-v6.pdf](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2023-v6.pdf); [Demonstracao_Financeira_FGTS_2025.pdf](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2025.pdf).

### Figura 8 — Déficit habitacional nacional e mudanças de base estatística

- **Período:** 2007–2024; 2020–2021 sem estimativa nesta série.
- **Unidade:** Milhões de domicílios.
- **Natureza:** Estimativas publicadas · metodologias distintas.
- **Base local:** `data/processed/deficit_fjp_historico.csv`.
- **Construção:** Totais nacionais publicados / 10⁶; linhas somente dentro de trechos comparáveis.
- **Hipóteses e limites:** Pnad anual 2007–2015; Censo 2010 isolado; PnadC reponderada 2016–2019; pontos 2022–2024 isolados pelas mudanças nos improvisados. Anos sem dado não são zero nem interpolados. Não identifica efeito causal do MCMV.
- **Fonte:** [FJP: catálogo de relatórios e planilhas](https://fjp.mg.gov.br/deficit-habitacional-no-brasil/); [FJP 2007, tabela retrospectiva 5.1 (cópia do relatório na UNMP)](https://www.unmp.org.br/wp-content/uploads/2009/06/Deficit%20Habitacional%20no%20Brasil%202007-Versao%20Final%20.pdf); [Ministério da Economia/SECAP, Boletim de Subsídios 10/2019, gráfico 1 (fonte FJP)](https://www.gov.br/gestao/pt-br/central-de-conteudo/publicacoes/boletins/boletim-subsidios/arquivos/2019/boletim-mensal-sobre-os-subsidios-da-uniao-2013-programa-minha-casa-minha-vida-edicao-10.pdf); [FJP: relatório 2024, seção 2 e tabela 1](https://drive.google.com/file/d/1wcGG-95LHqzhjXbtTvCnFh2XX2vL0xyW/view); [FJP: planilha 2016_2019](https://docs.google.com/spreadsheets/d/1y0c_oDcNpcq29fJyPAA4jtjDTAzij2MW/edit); [FJP: planilha 2023](https://docs.google.com/spreadsheets/d/1lQzsAuzhRCEJufiIEI_tVzO4vllcBT38/edit); [FJP: planilha 2024](https://docs.google.com/spreadsheets/d/1AwlL17JBmASv8Jurnkb6zhfXc0fzGQwp/edit).

### Figura 9 — Composição do déficit habitacional em 2022 e 2024

- **Período:** Edições de referência 2022 e 2024.
- **Unidade:** Milhões de domicílios.
- **Natureza:** Estimativas publicadas · componentes de cada edição.
- **Base local:** `data/processed/deficit_fjp_componentes_2022_2024.csv`.
- **Construção:** Habitação precária + coabitação + ônus excessivo com aluguel, cada componente da respectiva edição / 10⁶.
- **Hipóteses e limites:** Não aplicar proporções de 2022 ao total de 2024. A comparação não separa mudança real de mudança na mensuração dos improvisados.
- **Fonte:** [FJP 2022 · tabela 4, Brasil](https://repositorio.fjp.mg.gov.br/bitstreams/cc248796-b48a-404f-a4b9-ea931f898604/download); [FJP 2024 · tabela 1, p. 20](https://drive.google.com/file/d/1wcGG-95LHqzhjXbtTvCnFh2XX2vL0xyW/view).

### Figura 10 — Retorno da carteira habitacional e diferencial bruto frente à Selic

- **Período:** 2021–2025.
- **Unidade:** % a.a. no painel A; R$ bilhões correntes no painel B.
- **Natureza:** Dados contábeis e cenário de oportunidade bruto.
- **Base local:** `data/processed/custo_oportunidade_fgts.csv`.
- **Construção:** Saldo médio = (abertura + encerramento)/2. Retorno = receita/saldo médio. Selic = [Π(1+taxa mensal)−1]. Diferencial = saldo médio × Selic − receita.
- **Hipóteses e limites:** Carteira habitacional inteira, não exclusivamente MCMV. Inclui juros, encargos e atualização monetária. Preservar diferencial negativo de 2021. Selic não é alternativa equivalente em risco e prazo. Não é despesa de caixa; não somar aos descontos/equalização.
- **Fonte:** [FGTS — Demonstracao_Financeira_FGTS_2021.docx](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2021.docx); [FGTS — Demonstracao_Financeira_FGTS_2023-v6.pdf](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2023-v6.pdf); [FGTS — Demonstracao_Financeira_FGTS_2025.pdf](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2025.pdf); [BCB SGS 4390 — Selic acumulada no mês](https://dadosabertos.bcb.gov.br/dataset/4390-taxa-de-juros---selic-acumulada-no-mes); [Ipeadata — via de acesso à Selic do BCB (BM12_TJOVER12)](https://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='BM12_TJOVER12')).

### Figura 11 — Variação efetiva do caixa e fluxo de manutenção

- **Período:** DFC 2023–2025.
- **Unidade:** R$ bilhões de dezembro de 2025.
- **Natureza:** DFC observada e fluxo de manutenção calculado.
- **Base local:** `data/processed/sim_dfc_reconciliacao.csv`, `data/processed/sim_ipca_mensal.csv`.
- **Construção:** Variação efetiva = caixa final − inicial. Manutenção = depósitos − saques + operacional + juros de títulos + outros investimentos. Fator = IPCA dez./2025 / média mensal anual.
- **Hipóteses e limites:** Manutenção exclui transferência PIS/PASEP, resgates líquidos de principal e recebimentos de investimentos permanentes. Mantém juros recebidos; não duplicar totais e rubricas da DFC.
- **Fonte:** [FGTS · DF 2023, DFC Controladora](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2023-v6.pdf); [FGTS · DF 2025, DFC Controladora](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2025.pdf); [IBGE · IPCA mensal, SIDRA 1737](https://api.sidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/202301-202512).

### Figura 12 — Saldos indicativos sob fluxos reais constantes

- **Período:** 2025–2040; fluxos calibrados em 2023–2025.
- **Unidade:** R$ bilhões de dezembro de 2025.
- **Natureza:** Cenários calculados · teste de esforço.
- **Base local:** `data/processed/sim_trajetorias.csv`, `data/processed/sim_sustentabilidade.csv`, `data/processed/sim_parametros.json`.
- **Construção:** Saldo(t) = 33,466156 + (ano−2025) × fluxo anual real do cenário.
- **Hipóteses e limites:** Sete cenários: média 2023–2025; repetição de 2025; depósitos −5%; saques +5%; recebimentos −5%; choques combinados; liberações e descontos +10%. Choques permanentes sobre a média; fluxos reais constantes. Região negativa é financiamento não coberto, não operação efetiva com caixa negativo ou previsão de insolvência.
- **Fonte:** [FGTS · DF 2023, DFC Controladora](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2023-v6.pdf); [FGTS · DF 2025, DFC Controladora](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2025.pdf); [IBGE · IPCA mensal, SIDRA 1737](https://api.sidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/202301-202512).

### Figura 13 — Ajuste anual necessário para preservar o caixa real

- **Período:** Fluxos calibrados em 2023–2025; ajuste anual permanente.
- **Unidade:** R$ bilhões de dezembro de 2025 por ano.
- **Natureza:** Cenários calculados · mesmos sete da Figura 12.
- **Base local:** `data/processed/sim_sustentabilidade.csv`.
- **Construção:** Ajuste anual = máximo(0, −fluxo anual do cenário).
- **Hipóteses e limites:** Preservar caixa difere de consumir reserva inicial. Ajuste pode ser recurso externo ou mudança nos fluxos; não é transferência da União já autorizada. Abrange todo o FGTS.
- **Fonte:** [FGTS · DF 2023, DFC Controladora](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2023-v6.pdf); [FGTS · DF 2025, DFC Controladora](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2025.pdf); [IBGE · IPCA mensal, SIDRA 1737](https://api.sidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/202301-202512).

### Figura 14 — Escala anual média no horizonte de dez anos

- **Período:** Estoque FJP 2024; horizonte ilustrativo de 10 anos.
- **Unidade:** R$ bilhões de dezembro de 2025 por ano.
- **Natureza:** Cenário calculado · escala de contratação.
- **Base local:** `data/processed/sim_escala.csv`, `data/processed/sim_parametros.json`.
- **Construção:** Para cada recorte, N × 50% × parâmetro unitário / 10 anos. Parâmetros: FAR bruto 2024–2025; principal e subsídio FGTS F1 2023–2025.
- **Hipóteses e limites:** Comparação dos dois recortes: total e sem ônus com aluguel. 50% FAR/50% FGTS; focalização 100%. Três medidas separadas: FAR bruto, crédito reembolsável e subsídio registrado. Divisão aritmética não é cronograma de caixa nem VP; custo líquido FAR fica na Figura 1A e no simulador. Custo econômico integrado da financiada permanece pendente.
- **Fonte:** [FGTS · DF 2023, DFC Controladora](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2023-v6.pdf); [FGTS · DF 2025, DFC Controladora](https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2025.pdf); [IBGE · IPCA mensal, SIDRA 1737](https://api.sidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/202301-202512); [FJP 2022 · tabela 4, Brasil](https://repositorio.fjp.mg.gov.br/bitstreams/cc248796-b48a-404f-a4b9-ea931f898604/download); [FJP 2024 · tabela 1, p. 20](https://drive.google.com/file/d/1wcGG-95LHqzhjXbtTvCnFh2XX2vL0xyW/view); [MCMV Financiado com FGTS/FS — dados analíticos](https://www.cidades.gov.br/images/stories/ArquivosSNH/ArquivosZIP/mcmv_financ_analitico_20260724.zip); [MCMV Financiado com FGTS/FS — dados analíticos](https://www.cidades.gov.br/images/stories/ArquivosSNH/ArquivosZIP/mcmv_financ_analitico_20260724.zip); [MCMV Subsidiado — Empreendimentos](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/habitacao/programa-minha-casa-minha-vida/arquivos/mcmv_subsidiado_202606302.zip).

## Integração do patch e conferência cruzada

`figura_far_dashboard.patch` foi inspecionado e `git apply --check` confirmou incompatibilidade de contexto e nomes (`fmt`/`params` versus `br`/`p`). Seu conteúdo foi integrado sem substituir a versão atual: quatro cenários fixos, barra horizontal, referência de valor bruto, fórmula, tabela, download e seis gráficos na abertura. A fórmula FAR agora é compartilhada em `dashboard/far.py`; a Figura 1A aparece tanto na abertura quanto no catálogo.

- Figura 1: R$ 44.045,94 e R$ 8.177,23 por contrato nas Faixas 1 e 2, **valores correntes** de 2023–2025; zeros registrados nas Faixas 3/4 não excluem apoio via juros.
- Figura 1A: R$ 159.257,41; R$ 166.801,30; R$ 168.310,08; R$ 174.345,19 nos quatro cenários. O primeiro é alta recuperação, não média nacional.
- Figura 3: 452.592 operações em 2023 e 659.127 em 2025. Mesma base/denominadores nas Figuras 1, 3 e 4.
- Figura 9: componentes somam 6.215.313 em 2022 e 5.773.983 em 2024. Os componentes de 2024 já estavam registrados em `docs/simulacoes.md` e no documento; foram transcritos para CSV com proveniência, sem distribuição proporcional de 2022.
- Figura 10: diferencial −R$ 2,22 bi em 2021 e R$ 42,14 bi em 2025; receita de R$ 36,19 bi e retorno de 6,62% em 2025.
- Figuras 11–13: manutenção real de R$ 15,72 bi, −R$ 3,76 bi e −R$ 7,58 bi; média R$ 1,46 bi; caixa inicial R$ 33,466156 bi; ajuste combinado R$ 21,71 bi/ano.
- Figura 14: total: FAR bruto R$ 50,33 bi/ano; crédito R$ 37,70 bi/ano; subsídio registrado R$ 13,47 bi/ano. Sem aluguel: R$ 19,06; R$ 14,27; R$ 5,10 bi/ano. Não somar como total fiscal.
- Árvore e simuladores: principal FGTS R$ 130.590,25 e subsídio registrado R$ 46.649,58 são valores **reais de dezembro de 2025**; por isso diferem dos R$ 123,6 mil/R$ 44,0 mil correntes no capítulo descritivo. FAR bruto R$ 174.345,19 e líquido de referência R$ 159.257,41 permanecem iguais. A árvore recebeu referência ao documento conferido; não foi necessário alterar o argumento ou esses parâmetros.
- O histórico resumido da abertura passou a usar as mesmas quebras da Figura 8, sem unir 2019 aos pontos de 2022–2024. A reprodução separa PNAD e Censo sem continuidade artificial.

## Limitações identificadas

A imagem da Figura 4 está ausente no arquivo-fonte, embora a legenda e os dados permitam reproduzir a medida. Não é possível aferir sua aparência original. A validação de fontes desta atualização confrontou o documento fornecido, as bases versionadas, seus metadados e os scripts; não substituiu as extrações oficiais nem criou nova edição de dados. A revisão dos juros mantém a tabela histórica citada no documento, não afirma atualização normativa posterior à consulta.

Perdas da financiada, tributos, juros líquidos de equalização, calendário mensal e safras continuam sem mensuração integrada. Essas lacunas não foram preenchidas com dados sintéticos. Custo em VP, compromisso bruto, principal e liquidez continuam em contas distintas.

## Verificação

`python -m unittest discover -s tests -v`: inventário de todas as legendas, valores publicados, fórmula FAR e cenários, componentes FJP, quebras metodológicas, diferencial negativo, reconciliação da DFC, sete trajetórias e aportes, dois recortes da escala e navegação por todas as 15 entradas com download.

Resultado local: **10 testes passaram**. Ambiente temporário criado a partir
do Python do projeto neste Mac (Python 3.9, Streamlit 1.50, Plotly 7.1 e
requirements.txt); implantação mantém seu runtime Python 3.11. O código de
largura dos gráficos aceita as APIs de ambas as versões do Streamlit.
Conferência no Chrome local: 15 entradas no índice; Figuras 1A, 9, 10 e 14
abertas e inspecionadas visualmente, sem exceções.
