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
