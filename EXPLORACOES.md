# Gráficos exploratórios para a caracterização do programa

Nas três abas com dados, selecione **Explorações e hipóteses**. Os gráficos essenciais continuam disponíveis. As abas FJP e SINAPI/INCC continuam pendentes: suas bases ainda não estão incorporadas ao repositório.

## Ministério das Cidades

1. Participação das fontes no volume registrado.
2. Composição anual das operações por código de faixa.
3. Número de contratos por ano e faixa.
4. Subsídio médio registrado por ano e faixa.
5. Valor médio financiado por operação.
6. Incidência de subsídio registrado positivo.
7. Concentração dos contratos versus concentração dos subsídios.
8. Subsídios registrados por fonte (FGTS e OGU), separados da fonte de crédito.

O primeiro gráfico deriva da tabela original. Os outros sete usam nova agregação da mesma base analítica de 24/07/2026, com 7.607.363 operações após o filtro de programas original. A contagem é de operações, não pessoas únicas. Os 64 grupos por ano, fonte e código são publicados; os microdados não são versionados.

Os filtros de período do primeiro gráfico e dos contratos são independentes e identificados pela posição. 2026 é parcial e fica excluído por padrão. A tabela de contratos tem cobertura de 100% nas quatro rubricas de subsídio nesta extração, mas o processamento preserva a distinção entre ausência e zero para futuras reproduções.

## FGTS

9. Saldo de arrecadação menos saques.
10. Saques como proporção da arrecadação.
11. Composição percentual das cinco despesas da DRE.
12. Evolução nominal dessas despesas.
13. Trajetórias das participações das modalidades de saque (somente 2020–2023).
14. Mapa de sensibilidade estática da arrecadação líquida a quedas de arrecadação e altas de saques.

O mapa não representa o caixa total nem a solvência do FGTS. A DRE não substitui o orçamento/aplicações por setor. As participações dos saques não foram multiplicadas pelo total da DFC, pois seria necessário conciliar os universos das duas tabelas.

## Emprego formal

15. Pessoas com carteira e demais ocupados, em milhões.
16. Crescimento das pessoas com carteira e do total de ocupados, base 100.
17. Variação da participação com carteira contra o mesmo trimestre do ano anterior, em pontos percentuais.
18. Sensibilidade da contribuição potencial a mudanças de participação com carteira e salário médio.

Demais ocupados não equivale a informais nem a pessoas jurídicas. Os exercícios não identificam causalmente pejotização. A simulação mantém população ocupada, alíquota e recolhimento constantes e não é previsão.

## Pontos de revisão para o primeiro retorno

- Seção 3.4 da v07: a faixa de R$ 22–36 bilhões para todos os anos após 2020 não corresponde à tabela. Em 2022 o saldo é R$ 1,875 bilhão. Em 2021 são R$ 21,676 bilhões; em 2025, R$ 22,150 bilhões.
- Seção 3.2: cerca de R$ 71 mil por unidade FAR é valor contratado por unidade, uma proxy, enquanto os contratos usam rubricas de subsídio. A comparação não mensura o mesmo conceito de custo.
- Os rótulos de faixa têm correspondência inferida no projeto. A evolução por faixa é exploratória e exige validar o dicionário e as mudanças de tetos antes de concluir mudança do público atendido.
- A série denominada OGU na figura original é uma proxy de empreendimentos subsidiados. Não pode ser interpretada como execução orçamentária anual da União. Ausência de registro não comprova execução zero.
- Despesas realizadas do FGTS não respondem ao pedido de orçamento/aplicações em habitação, saneamento e infraestrutura. Essa lacuna permanece explícita na capa e na aba.
- Subsídios registrados nos contratos e descontos na DRE têm critérios e períodos contábeis diferentes. Não precisam coincidir; não somar as duas medidas.
- A hipótese de restrição do FGTS exige amortizações, retornos dos ativos, passivos, remuneração e desembolsos. As sensibilidades apresentadas são preparatórias, não o modelo completo da Seção 5.

## Reprodução e validação

Após o download original da base analítica:

```sh
python scripts/process_exploracao_contratos.py
python scripts/validate_exploracao.py
```

O primeiro script documenta fontes e premissas em `exploracao_contratos.meta.json`. O segundo reconcilia os valores de financiamento com a tabela original, confere os componentes de subsídio e executa as abas, os 18 gráficos e filtros extremos com o AppTest do Streamlit. Cada gráfico permite baixar sua tabela filtrada.
