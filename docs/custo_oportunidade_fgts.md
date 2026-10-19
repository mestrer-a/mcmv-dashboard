# Custo registrado e custo de oportunidade do FGTS

Atualização de 19/10/2026. O dashboard agora contém uma primeira estimativa anual **bruta** para a carteira habitacional do FGTS, de 2021 a 2025, e as taxas históricas dos contratos. Não é uma medida líquida nem exclusiva do MCMV.

## Implementação disponível

Na aba **FGTS**, três gráficos em colunas mostram (1) retorno contábil bruto versus Selic, (2) receita reconhecida versus receita alternativa e (3) descontos concedidos na DRE versus diferencial de retorno estimado. Todos respondem ao recorte temporal e ao ajuste da Selic em pontos percentuais. Os dados e parâmetros podem ser baixados em CSV.

Usamos a linha habitacional da movimentação da Nota 9 das DF: receita de juros/encargos/atualização monetária, abertura e encerramento **brutos**, sem provisões. Em 2021, adicionamos a provisão de 529.595 (R$ milhares) ao encerramento líquido de 367.691.707, chegando a 368.221.302. O script verifica a identidade abertura + liberações líquidas + receita + demais movimentos = encerramento. Em 2022–2025 os saldos brutos estão diretamente na movimentação. Os saldos de um exercício coincidem com a abertura do seguinte.

`Diferencial = média(saldo inicial bruto, saldo final bruto) × (Selic anual + ajuste) − receita reconhecida`.

A Selic é composta pelos 12 meses, em vez de usar a meta de dezembro. A API direta do BCB falhou na consulta; os valores foram obtidos do **Ipeadata BM12_TJOVER12**, que informa BCB como fonte e a mesma unidade mensal do SGS 4390. Resposta original preservada localmente, valores mensais versionados em `selic_mensal.csv`. Uma referência ajustada em ± pontos percentuais é um cenário, não dado observado.

O resultado é bruto: não desconta custos, perdas, impostos ou remuneração de cotistas. Não supõe equivalência de prazo, risco ou admissibilidade legal entre a carteira e aplicações à Selic. Valores negativos são preservados: indicam receita superior à referência naquele ano, não ausência de subsídios. Não estimamos 2020 sem a abertura correspondente, nem 2026 sem DF anual.

Os **descontos da DRE abrangem o Fundo inteiro**, enquanto a estimativa usa a carteira habitacional. São exibidos lado a lado para comparar ordens de grandeza; não são somados. Tampouco substituem a soma de desconto/equilíbrio por safra de contratação do MCMV: são universos e momentos de reconhecimento distintos.

Na aba **Programa e subsídios**, as taxas iniciais foram agregadas por mês, fonte e código de faixa, com ponderação pelo principal e cobertura explícita. A convenção nominal/efetiva não foi confirmada pelo dicionário SNH; há opção de leitura informada ou de conversão sob hipótese nominal anual com capitalização mensal. A **série BCB 20772 não pôde ser obtida**, portanto o dashboard exibe somente taxas contratadas, sem inventar taxa de mercado ou diferencial. A implementação comporta a comparação ponderada no mesmo mês quando a fonte for recuperada; o CSV de mercado está vazio, com cabeçalho e ausência documentada.

Reprodução desta versão: `python scripts/process_custo_oportunidade.py --market-unavailable`. Omitir essa opção somente quando o SGS 20772 estiver acessível; `--skip-contracts` evita reler os microdados. Validação: `python scripts/validate_custo_oportunidade.py` e `python scripts/validate_dashboard.py`.

## O que existe no repositório

Temos descontos e equilíbrio registrados por contrato e agregados por ano; despesas contábeis, fluxos de caixa e estoques do FGTS de 2020 a 2025. A base analítica original também contém `num_taxa_juros`, `txt_sistema_amortizacao`, data de contratação, valor financiado, renda, região e condição de cotista. As taxas iniciais agora estão agregadas em `juros_contratos_mensal.csv`. A tabela normativa de junho de 2026 não representa as taxas contratadas no passado.

O cabeçalho da base analítica não contém prazo, saldo devedor ao longo do tempo, pré-pagamentos, inadimplência, fluxo de pagamentos ou remuneração que cabe exclusivamente ao FGTS. Logo, há insumos para uma comparação histórica de taxas, mas não uma medida completa observada do custo de oportunidade anual do Fundo.

## Três perguntas distintas

1. **Benefício ao mutuário:** quanto ele pagaria em financiamento de mercado comparável? Comparar a taxa contratada com a taxa de referência no mês de contratação, mantendo principal, prazo, risco, indexador e amortização coerentes. É um contrafactual condicionado; não garante que essa família conseguiria o mesmo crédito no mercado.
2. **Custo de oportunidade do FGTS:** qual retorno líquido o Fundo deixa de obter ao alocar recursos nessa carteira em vez de uma aplicação alternativa admissível? A taxa final cobrada do mutuário inclui remunerações de agentes financeiros e não pode ser tomada integralmente como receita do Fundo.
3. **Custo de captação/resultado contábil e caixa:** o que o FGTS remunera aos trabalhadores, distribui como resultado, gasta e paga efetivamente? É necessário para sustentabilidade, mas não é igual ao retorno alternativo perdido. Uma carteira pode ter margem contábil positiva e custo de oportunidade positivo ao mesmo tempo.

O contrafactual de retorno do Fundo deve respeitar as alternativas e restrições legais de alocação, prazo, liquidez, risco e indexação. Selic é uma referência de sensibilidade para a alternativa financeira, não uma taxa automaticamente equivalente a um crédito imobiliário de décadas.

## Como construir o histórico

**Fluxo anual da carteira:** uma aproximação seria `custo_t = saldo médio da carteira elegível_t × (retorno alternativo líquido_t − retorno líquido da carteira_t)`. Preferir saldos e receitas mensais. A média entre dezembro anterior e dezembro atual só deve entrar identificada como aproximação. Empréstimos contratados no ano são fluxo de concessões e não substituem o estoque médio. Se usarmos a carteira habitacional total das DF, o resultado precisa ter esse nome: não é automaticamente MCMV.

**Custo das novas concessões:** calcular o valor presente dos fluxos que cabem ao Fundo, descontados por uma curva alternativa compatível com os vencimentos. A diferença entre desembolso e valor presente dos recebimentos esperados mede o equivalente de concessionalidade na origem. Somar por safra de contratação produz um histórico de compromissos assumidos, e não de despesa de caixa daquele ano. Para um exercício prospectivo, não fixar a Selic de um único mês por 30 anos nem usar taxas futuras realizadas como se fossem conhecidas na contratação.

**Etapa já viável com os dados:** agregar as taxas efetivamente contratadas por mês e faixa, ponderadas pelo principal, informando cobertura e valores inválidos; confrontar com benchmark do BCB no mesmo mês. Antes da comparação, verificar no dicionário a convenção nominal/efetiva de `num_taxa_juros`, anualizar de modo consistente e harmonizar a TR e outros encargos. O SGS 20772 começa em março de 2011; não preencher 2009–2010 com taxas de anos posteriores. Uma média simples de taxas mensais não é a taxa anual ponderada por concessões.

**Dados adicionais para valores em reais:** prazos e fluxos dos contratos ou hipóteses explícitas de amortização/antecipações; saldos por modalidade; remuneração dos agentes; retorno da carteira que cabe ao FGTS; receita de correção monetária separada de juros; perdas e custos, conforme a definição líquida escolhida. Uma simulação com prazo assumido é possível, mas deve ser apresentada como estimativa modelada, com sensibilidade.

Não adicionar mecanicamente esse valor aos descontos e ao equilíbrio já registrados: primeiro reconciliar fluxos e pagadores para evitar contar duas vezes a redução de encargos. Também não somar o valor presente por safra ao custo anual sobre o estoque. A simulação de prestação SAC existente continua ilustrativa e não foi reclassificada como custo ou subsídio implícito.

## Materiais localizados

- **Fioravante, Dea Guerra; Furtado, Bernardo Alves (2018). Crédito imobiliário.** Capítulo 6 de *Financiamento do desenvolvimento no Brasil*, Ipea, pp. 193–224. Discute subsídios, captação direcionada e custo de oportunidade. Serve à fundamentação conceitual; a pesquisa realizada não identificou nele uma série anual pronta de custo econômico do MCMV/FGTS que possa ser importada para este dashboard. [Capítulo no Ipea](https://portalantigo.ipea.gov.br/agencia/images/stories/PDFs/livros/livros/181105_livro_financiamento_desenvolvimento_cap06.pdf).
- **Nascimento, Paulo A. Meyer M.; Longo, Gustavo Frederico (2016). Qual o custo implícito do FIES para o contribuinte brasileiro?** *Radar*, n. 46, Ipea. Aplica valor presente dos reembolsos para quantificar o subsídio de crédito. Referência de método para adaptar; os resultados numéricos sobre Fies não são transferíveis ao FGTS. [Artigo e resumo](https://repositorio.ipea.gov.br/items/667c1871-d756-475f-8e9f-8f544922dcbf).
- **Banco Central, SGS 20772.** Taxa média das novas operações de financiamento imobiliário de pessoas físicas com taxas de mercado; mensal, expressa em % a.a., ponderada pelo valor das concessões, desde março de 2011. Candidato ao benchmark do mutuário; não é rentabilidade líquida disponível ao FGTS, nem controle de risco equivalente ao público MCMV. [Metadados oficiais](https://dadosabertos.bcb.gov.br/dataset/20772-taxa-media-de-juros-das-operacoes-de-credito-com-recursos-direcionados---pessoas-fisicas---fi).
- **Ministério da Economia/SECAP (2019). Boletim mensal sobre os subsídios da União — PMCMV, edição 10.** Material de contexto sobre desenho, fontes e subsídios; não substitui a apuração do custo de oportunidade do Fundo. [Boletim](https://www.gov.br/gestao/pt-br/central-de-conteudo/publicacoes/boletins/boletim-subsidios/arquivos/2019/boletim-mensal-sobre-os-subsidios-da-uniao-2013-programa-minha-casa-minha-vida-edicao-10.pdf).

## Implicação para a dissertação

Apresentar separadamente o custo registrado, a vantagem financeira ao mutuário e o custo de oportunidade estimado do Fundo. A avaliação de sustentabilidade deve continuar reconciliando estoque, retorno da carteira, novas concessões, descontos, arrecadação e saques. Nenhum diferencial de taxa, isoladamente, demonstra insolvência ou o efeito do programa sobre o déficit habitacional.
