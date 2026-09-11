# Revisão de setembro de 2026

## Implementado

- Balanços 2020–2025, Controladora, com revisões de 2021–2022 identificadas; ativo e passivo reconciliados.
- Ponte DFC 2024–2025, distinguindo variação de caixa e contribuição líquida.
- Total do déficit de referência 2024 confirmado em divulgação oficial. Metodologia atual: três componentes.
- Navegação lateral, escolha da pergunta, filtros persistentes, fontes agrupadas no topo, séries Plotly com hover unificado, zoom e exportação. As 18 explorações anteriores foram preservadas.
- Marcos históricos no gráfico por fonte; comparação de participação nos contratos e nos subsídios registrados.
- Correção da leitura da DRE: despesas contábeis não são orçamento de aplicações por setor.

## Limitações ainda abertas

A busca do repositório FJP retornou erro; os endereços de publicação e tabelas da edição 2024 retornaram 403/404 após a reorganização do portal. A cartilha metodológica e o total puderam ser verificados, mas as tabelas originais por renda e componente não foram recuperadas. Não foram criadas aberturas numéricas ou arquivos vazios com aparência de base concluída. O confronto quantitativo déficit × renda e o custo por componente dependem dessas tabelas.

Não foram executadas projeções completas de solvência, déficit ou custo implícito. FAR por unidade é proxy distinta do subsídio registrado no financiamento. Faixas 3/4 podem ter benefício de juros mesmo com subsídio registrado zero. Classificação histórica não equivale aos tetos atuais.

## Reprodução

```sh
python scripts/download_balanco.py
python scripts/process_balanco_fgts.py
python scripts/process_deficit_fjp.py
python scripts/validate_dashboard.py
streamlit run dashboard/app.py
```

Cada CSV novo possui metadados de fonte e método. Os documentos baixados ficam em data/raw (ignorados pelo git); os balanços registram também hashes SHA-256 das fontes consultadas.
