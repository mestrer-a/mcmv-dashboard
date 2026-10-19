# Sustentabilidade e escala de atendimento — 19/10/2026

## Reprodução

`python scripts/build_simulations.py` (pandas e numpy).

O script lê os insumos versionados, verifica a DFC e gera os arquivos `sim_*`.
Não usa rede, não altera dados de origem e mantém precisão integral nos cálculos.
Todos os resultados monetários são reais de dezembro de 2025, salvo a DFC de
origem, expressa em R$ milhares correntes. 2026 parcial não entra na calibração.

## Fontes

- FGTS, Demonstrações Financeiras 2023 e 2025, DFC da **Controladora**.
  https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2023-v6.pdf
  https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2025.pdf
- IPCA, IBGE/SIDRA, tabela 1737, variável 2266, Brasil, janeiro/2023–dezembro/2025.
  https://api.sidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/202301-202512
- FJP, Déficit habitacional no Brasil 2024, tabela 1: 5.773.983 domicílios;
  habitação precária 1.156.834; coabitação 1.029.372; aluguel 3.587.777.
  https://drive.google.com/file/d/1wcGG-95LHqzhjXbtTvCnFh2XX2vL0xyW/view
- FJP 2022: 6.215.313; sem aluguel 2.972.533. Edição oficial:
  https://drive.google.com/file/d/13FL-MVsULmFMjkQb1nQsYzO2JVhLQvwz/view
- Contratos: `exploracao_contratos.csv`, FGTS, código Faixa 1, 2023–2025;
  FAR: `far_anual.csv`, 2024–2025. Ver metadados desses arquivos para filtros
  administrativos. FAR 2023 está ausente na extração, não é execução zero.

## Dicionário da DFC

Entradas positivas; saídas negativas, exceto `pis_transfer`, saída apresentada
em magnitude positiva e subtraída explicitamente. Todos os valores da entrada
estão em R$ milhares.

| Coluna | Significado |
|---|---|
| deposits / withdrawals | Arrecadação / saques |
| credit_new / credit_receipts | Novos empréstimos e financiamentos / recebimentos |
| title_op | Recebimentos operacionais de títulos e recuperação de despesas |
| other_loans | Recebimentos de outros empréstimos |
| admin / discounts | Administração / descontos pagos |
| cash_interest | Remuneração de caixa e equivalentes recebida |
| other_op | Demais fluxos operacionais |
| bond_buy / bond_principal | Aquisição / recebimento de principal de títulos |
| bond_interest | Remuneração recebida de títulos |
| permanent / other_inv | Recebimentos de investimentos permanentes / demais investimentos |
| op_total / inv_total | Totais operacionais / de investimento da DFC |
| pis_transfer | Transferência PIS/PASEP ao Tesouro |
| cash_start / cash_end | Caixa no início / encerramento do ano |

Em 2023, `title_op = 1.720.599 + 6.825`, agregando recebimento de títulos e
recuperação de despesas. A soma das rubricas operacionais e a das rubricas de
investimento são verificadas contra seus totais. A soma dos três fluxos deve
ser idêntica à variação dos saldos de caixa. O script interrompe se houver erro.

## Normalização e cenários

Fator anual = IPCA de dez./2025 / média mensal dos índices do ano. É uma
aproximação explícita para fluxos anuais sem cronograma mensal. Quantidades
não são corrigidas. Caixa inicial é o saldo de 31/12/2025, R$ 33,466156 bilhões.

Fluxo de manutenção = depósitos − saques + fluxo operacional + juros de
títulos + outros investimentos. Exclui PIS/PASEP, resgates líquidos de
principal e recebimentos de investimentos permanentes. Não trata liquidação
de ativos como renda perpétua. Conserva receitas sob hipótese de manutenção
da capacidade de geração, sem modelo de recomposição da carteira por safra.

Referência: média real 2023–2025. Alternativa: repetir 2025. Choques permanentes
de −5% nos depósitos, +5% nos saques, −5% nos recebimentos, isolados e
combinados. Expansão: +10% das liberações e descontos pagos. Não se aplicam
juros adicionais ao caixa, evitando repetir remuneração já contida na DFC.

Saldo indicativo = caixa inicial + horizonte × fluxo anual.
Necessidade depois de consumir caixa = max(0, −saldo).
Ajuste anual para preservar caixa = max(0, −fluxo anual).
Tempo contínuo até limite = caixa inicial / saída líquida anual, se negativa.

Saldos negativos são necessidades não cobertas, não saldos operacionais
possíveis. Não há previsão de insolvência patrimonial ou data de esgotamento.
Títulos e patrimônio não são adicionados à disponibilidade inicial. Reduzir
novas aplicações alivia o caixa no primeiro momento, mas altera receitas
futuras; o modelo não recomenda um corte permanente a partir dessa identidade.
As necessidades abrangem o FGTS, não exclusivamente o MCMV.

## Atendimento habitacional

Parâmetro unitário = soma de valores corrigidos / soma de quantidades.
Principal e subsídio da Faixa 1 excluem Fundo Social. Subsídio registrado
inclui equilíbrio; não necessariamente foi pago no ano da contratação.

N = estoque / focalização. Com participação a de FAR:

- FAR bruto = N × a × parâmetro FAR;
- crédito FGTS = N × (1 − a) × principal médio;
- subsídio registrado = N × (1 − a) × subsídio médio.

Cada montante é dividido separadamente por 5, 10 ou 15 anos. Não se produz
total fiscal, valor presente ou cronograma executivo. Modalidades: 100% FAR,
50/50 e 100% FGTS Faixa 1. Focalização: 100%, 75%, 50%, estritamente hipotética.
As combinações não presumem elegibilidade de todas as famílias ao crédito.
Estoques 2024 e 2022, total e sem aluguel; não se aplicam proporções de renda
de 2022 ao total de 2024. Não há geração de novas necessidades no exercício.

## Limitações

Análise descritiva não identifica efeito causal do programa no déficit.
Mudanças metodológicas da FJP impedem tratar a série inteira como homogênea.
Não estimados: custo tributário, perda esperada por contrato, benefício de
juros líquido de equalização, maturação das safras de crédito, custos de
alternativas de locação, cronogramas de obras e novos ingressos no déficit.
O diferencial bruto de retorno da carteira habitacional frente à Selic está
na página FGTS: não somar ao subsídio registrado nem ao aporte de caixa.
