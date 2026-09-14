# Fontes de dados — mcmv-dashboard

Cada entrada: nome, URL de origem, URL de download direto (quando distinta), data de acesso, tamanho no momento do acesso.

## Portal de Dados Abertos do Ministério das Cidades

Dataset "catálogo" (metadados, não hospeda os arquivos em si):
https://dadosabertos.cidades.gov.br/dataset/dados-do-programa-minha-casa-minha-vida-pmcmv

Os 3 recursos desse dataset no CKAN apontam para uma página do gov.br que hospeda os arquivos reais:
https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/habitacao/programa-minha-casa-minha-vida/bases-de-dados-do-programa-minha-casa-minha-vida

### 1. MCMV Subsidiado — Empreendimentos (nível de projeto, ~58 mil empreendimentos, recursos do OGU/FAR/FDS conforme modalidade)
- Download: https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/habitacao/programa-minha-casa-minha-vida/arquivos/mcmv_subsidiado_202606302.zip
- Formato: CSV (zipado)
- Tamanho: 1.177.997 bytes (~1,1 MB) comprimido
- Data de acesso: 2026-09-10

### 2. Contratos MCMV-Financiado com recursos do FGTS — dados SINTÉTICOS (por município/ano)
- Download: https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/habitacao/programa-minha-casa-minha-vida/arquivos/mcmv_financ_sintetico_20260724_v2.zip
- Formato: CSV (zipado)
- Tamanho: 10.135.340 bytes (~9,7 MB) comprimido
- Data de acesso: 2026-09-10
- Limitação identificada: `vlr_subsidio` é o subsídio total (OGU **ou** FGTS somados) — não separa por fonte nem por programa (não dá pra isolar "Fundo Social" aqui).

### 3. Contratos MCMV-Financiado com recursos do FGTS/FS — dados ANALÍTICOS (nível de contrato)
- Download: https://www.cidades.gov.br/images/stories/ArquivosSNH/ArquivosZIP/mcmv_financ_analitico_20260724.zip
- Formato: CSV (zipado)
- Tamanho: 200.671.574 bytes (~191 MB) comprimido — **base pesada, aguardando decisão sobre necessidade antes de baixar**
- Data de acesso: 2026-09-10
- Único nível que separa subsídio por fonte (`vlr_subsidio_desconto_fgts`, `vlr_subsidio_desconto_ogu`, `vlr_subsidio_equilibrio_fgts`, `vlr_subsidio_equilibrio_ogu`) e por programa (`txt_programa_fgts`, que inclui o valor "Fundo Social" entre outros: Apoio à Produção, Carta de Crédito Associativo, Carta de Crédito Individual, Classe Média, Faixa Estendida, Fundo Social, Pró-Cotista).

### Dicionário de dados (todas as bases acima)
- Download: https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/habitacao/arquivos-1/Dicionarios_SNH_2025_10_09.pdf
- Versão 2.4, de 09/10/2025
- Tamanho: 233.129 bytes
- Data de acesso: 2026-09-10
- Salvo localmente em: data/raw/Dicionarios_SNH_2025_10_09.pdf (a copiar)

## Dataset "Execução Orçamentário-Financeira da Habitação" (candidato a complementar, NÃO usado ainda)
https://dadosabertos.cidades.gov.br/dataset/execucao-orcamentario-financeira-da-habitacao
- Contém rubrica por Programa (FAR; FDS; PNHR; FNHIS; PNHU; OFERTA PÚBLICA; OFERTA PÚBLICA - NOVO), mas **cobre apenas o ano de 2024** — não é série histórica. Mantenedora: Nilza Emy Yamasaki (contato do dataset, não confirmado por nós).
- Recursos: ExecucaoOrcamentarioFinanceiraSNH2024.csv (1.576 bytes), ExecucaoOrcamentarioFinanceiraEmendasSNH2024.csv (5.729 bytes), Quantidade_UH_Subsidiadas_Emendas_Parlamentares_SNH.csv (1.819 bytes)
- Data de acesso: 2026-09-10

## Pendente de localizar (não buscado ainda)
- Orçamento do CCFGTS e Demonstrações Financeiras do FGTS (Agente Operador/Caixa)
- Acórdão TCU 270/2026 (pesquisa.tcu.gov.br)
- PNAD Contínua (sidra.ibge.gov.br) — formalização
- Novo Caged (pdet.mte.gov.br)
- Déficit habitacional — Fundação João Pinheiro (fjp.mg.gov.br/deficit-habitacional-no-brasil)
- SINAPI (IBGE) e INCC (FGV/IBRE)


## Balanço patrimonial do FGTS

Acesso: 2026-09-11. Processamento: `scripts/process_balanco_fgts.py`.

- Demonstracao_Financeira_FGTS_2021.docx: https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2021.docx
- Demonstracao_Financeira_FGTS_2023-v6.pdf: https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2023-v6.pdf
- Demonstracao_Financeira_FGTS_2025.pdf: https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2025.pdf

DF 2025 para 2024–2025; DF 2023 para 2021–2023, incluindo reapresentação; versão editável oficial de 2021 para 2020, pois o link PDF redirecionava em ciclo.


## Ponte do caixa do FGTS

Acesso: 2026-09-11. Processamento: `scripts/process_balanco_fgts.py`.

- Demonstracao_Financeira_FGTS_2021.docx: https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2021.docx
- Demonstracao_Financeira_FGTS_2023-v6.pdf: https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2023-v6.pdf
- Demonstracao_Financeira_FGTS_2025.pdf: https://www.fgts.gov.br/Paginas/downloads/relatorios/demonstracoes_financeiras/Demonstracao_Financeira_FGTS_2025.pdf

DF 2025 para 2024–2025; DF 2023 para 2021–2023, incluindo reapresentação; versão editável oficial de 2021 para 2020, pois o link PDF redirecionava em ciclo.


## Déficit habitacional total, referência 2024

Acesso: 2026-09-11. Processamento: `scripts/process_deficit_fjp.py`.

- Ministério das Cidades na Agência Gov, 29/04/2026: https://agenciagov.ebc.com.br/noticias/202604/minha-casa-minha-vida-contribui-para-o-menor-deficit-habitacional-da-historia-do-pais-afirma-ministro
- Cartilha metodológica FJP: https://drive.google.com/file/d/1ITXVvGuAs43gyQAVcwb_Z-P6XKGjtL1o/view

2024 é a referência mais recente identificada; total confirmado na divulgação oficial do Ministério. Não substitui as tabelas originais por renda e componente, ainda indisponíveis nos endereços consultados.


## Revisão de 13/09/2026 — déficit por renda e modalidades

- FUNDAÇÃO JOÃO PINHEIRO. Déficit Habitacional no Brasil 2022. Belo Horizonte: FJP, 2023, conforme ficha fornecida pelo autor. Acesso set/2026.
  Repositório: https://repositorio.fjp.mg.gov.br/handle/123456789/4262
  PDF: https://repositorio.fjp.mg.gov.br/bitstreams/cc248796-b48a-404f-a4b9-ea931f898604/download
  Tabelas 4 e 5, p. 30–32. CSV e script de transcrição fornecidos pelo autor, preservados sem reextração. Verificação desta revisão limitada à integridade e reconciliação interna.
- Referência 2022: 6.215.313 domicílios, única edição **integrada neste repositório** com renda × componente. Referência 2024: 5.773.983, divulgação do Ministério já documentada, sem tabelas desagregadas integradas. Nenhum prorrateio entre edições.
- Faixa 1 por modalidade: mesmas versões analítica (24/07/2026) e subsidiada (30/06/2026) documentadas acima. O ZIP subsidiado foi recuperado do mesmo URL oficial porque faltava na cópia local; não é atualização de base. `process_faixa1_modalidade.py` registra hashes, campos e exclusões.
- Orçamento operacional inicial 2026: Resolução CCFGTS 1.133/2025, Anexo IV, p. 5 do PDF:
  https://www.gov.br/cidades/pt-br/acesso-a-informacao/institucional/base-juridica/resolucoes/fgts/Res_CCFGTS_2025_1133.pdf
  Suplementação de descontos em setembro:
  https://www.gov.br/trabalho-e-emprego/pt-br/noticias-e-conteudo/2026/setembro/conselho-suplementa-r-500-milhoes-no-orcamento-do-fgts-para-subsidio-habitacional
  O gráfico reproduz a peça **inicial**, não orçamento atualizado/consolidado nem execução.

As pendências antigas de demonstrações, PNAD e abertura FJP acima foram parcialmente superadas. Permanecem pendentes execução setorial, OGU, Caged e índices de construção.
