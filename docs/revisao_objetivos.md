# Revisão de 31 de outubro de 2026

Referência: Dissertacao_Revisao_Objetivos.docx. A seção 4.4 e o capítulo 5 respondem ao custo estático do déficit e à capacidade anual de manutenção do FGTS.

## Resultados

- Déficit 2024 completo: R$ 523,3221 bilhões; sem ônus excessivo com aluguel: R$ 183,3947 bilhões.
- Principal separado: R$ 707,8358 bilhões / R$ 310,1806 bilhões.
- FAR líquido: R$ 161.757,62716084564; composição FAR na Faixa 1: 22,426479387559%.
- Recebimentos/liberações do FGTS: 72,0771%; margem média: R$ 1,459576 bilhão.

Valores em reais de dezembro de 2025. Resultados condicionais, não custo fiscal observado, solvência atuarial ou calendário de erradicação.

## Correções da auditoria

O cálculo preliminar aplicava médias globais de taxa antes do VP. Agora calcula por mês e fonte, com SAC comum e fator anual de IPCA, agregando depois. A SGS 20772 contém novas concessões imobiliárias de taxas de mercado com recursos direcionados. Não harmoniza riscos, indexadores e prazos.

Equilíbrio: o dicionário SNH v2.4 associa a rubrica à redução dos juros da família. A CAIXA descreve cobertura do diferencial de juros e taxa administrativa. Portanto, não é custo independente do benefício de juros. Referência conservadora: explícito + máximo(0, benefício − equilíbrio). Como o benefício supera o equilíbrio nas faixas, equivale a complemento + benefício. O apoio administrativo pode ficar de fora: não foi identificado separadamente. Não é custo líquido comprovado do FGTS. A soma sem dedução (R$ 610,5266 bi / R$ 210,2401 bi) fica apenas como diagnóstico da duplicação potencial, não como resultado adicional.

Prazo de 360 meses e convenção SNH nominal/12 não foram confirmados como condições de todos os contratos. Permanecem hipóteses, com sensibilidades a 240/420 meses e taxa efetiva. Não chamar de características observadas. Dicionário também lista SAC/Price/Sacre: SAC é cenário padronizado, não identificação da carteira.

A participação de FAR e FGTS usa o mesmo biênio e datas de assinatura. As extrações são atualizadas em 30/06/2026 e 24/07/2026. São unidades/contratos brutos, não entregas, beneficiários únicos ou quantidades líquidas de distratos. Essa diferença impede interpretar a participação como efetividade de atendimento. Compra Assistida excluída; sem FAR 2023 na extração.

A composição de renda 2022 é aplicada por componente a 2024, normalizada pela soma das faixas. Os limites de renda não são os de 2026. Acima da Faixa 3: parâmetro Faixa 4 como proxy, não prova de elegibilidade. Essa parcela custa R$ 9,67 bilhões nos dois recortes e é separada no Quadro 5.

A DFC fecha em cada ano. Fluxo de manutenção exclui transferência extraordinária PIS/PASEP, resgate líquido de principal dos títulos e recebimentos de investimentos permanentes; preserva juros e demais fluxos. A análise abrange o FGTS, não exclusivamente o MCMV ou a carteira habitacional. Caixa inicial de R$ 33,466156 bi é estoque de 31/12/2025.

O IBGE confirmou informalidade anual de 39,0% em 2024 e 38,1% em 2025 (release 30/01/2026). Não inferir explosão da informalidade ou causalidade de IVA sobre depósitos.

## Reprodução

`python scripts/calcular_revisao_objetivos.py`

`python -m unittest discover -s tests -v`

Figura 12 lê revisao_custo_deficit.csv, como o Word. Figura 13 lê sim_sustentabilidade.csv. Os IDs internos antigos foram preservados nos links existentes; a numeração exibida acompanha 1–13 no documento. Figuras antigas 11/12/14 permanecem como funções de exploração, fora do catálogo atual. O simulador FAR adicional não altera os resultados estáticos.

Fontes verificadas: SNH dicionário v2.4; BCB SGS 20772; CAIXA relatório FGTS 2015, seção descontos; IBGE PNAD anual 2025. A média DI é referência congelada de cenário, preservando a fonte secundária e seus limites no metadado.
