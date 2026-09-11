# Dicionário de dados — mcmv-dashboard

Fonte oficial completa: `data/raw/Dicionarios_SNH_2025_10_09.pdf` (Ministério das Cidades/SNH, versão 2.4, 09/10/2025). Este arquivo documenta apenas as colunas efetivamente usadas nos scripts de processamento, com as premissas de limpeza aplicadas.

## MCMV Subsidiado (Empreendimentos) — `mcmv_subsidiado_202606302.zip`
Nível: empreendimento/projeto (~58 mil).

| Coluna | Descrição oficial | Uso no projeto |
|---|---|---|
| `dt_assinatura` | Data de contratação do empreendimento habitacional | extrai o ano → eixo temporal |
| `txt_modalidade` | FAR; Entidades; Oferta Pública; Rural | referência (não usada para separar fonte — ver nota abaixo) |
| `val_contratado_total` | Valor total contratado, incl. suplementação | somado por ano → série "OGU" do Gráfico 1 |
| `txt_situacao_empreendimento` | Concluído; Não Concluído; Distratado/Cancelado | não filtrado no Gráfico 1 (valor contratado independe do status de entrega) |

**Nota metodológica:** esta base não tem coluna explícita de fonte orçamentária (OGU vs FDS). Está sendo tratada integralmente como proxy de "OGU" no Gráfico 1 porque é o universo de empreendimentos subsidiados fora do financiamento direto com FGTS — é uma aproximação, não uma separação confirmada por fonte oficial. Ficou pendente localizar uma fonte que mapeie `txt_modalidade` → fonte orçamentária exata.

## Contratos MCMV-Financiado com FGTS — dados sintéticos — `mcmv_financ_sintetico_20260724_v2.zip`
Nível: agregado por município/ano/mês. Cobre 2009–2026.

**Divergência encontrada:** o dicionário PDF documenta uma coluna `num_ano_financiamento`, mas o CSV real tem `num_ano` + `num_mes` separados, e também traz `txt_compatibilidade_faixa_renda` (códigos "1"/"2"/"3"/"4"/vazio — sem o dicionário de código→faixa, o mapeamento para "Faixa 1/2/3" não está confirmado) que não consta na tabela do dicionário para esta base. Colunas reais (separador `;`, decimal com ponto):
`data_referencia; cod_ibge; txt_municipio; mcmv_fgts_txt_uf; txt_regiao; num_ano; num_mes; qtd_uh_financiadas; vlr_financiamento; vlr_subsidio; txt_compatibilidade_faixa_renda`

| Coluna | Uso no projeto |
|---|---|
| `num_ano` | eixo temporal |
| `vlr_financiamento` | **não usado no Gráfico 1** — substituído pela base analítica para permitir separar Fundo Social |
| `vlr_subsidio` | subsídio total (OGU **ou** FGTS somados), não decompõe por fonte — por isso não serve ao Gráfico 1 |

## Contratos MCMV-Financiado com FGTS/FS — dados analíticos — `mcmv_financ_analitico_20260724.zip`
Nível: contrato individual. Único nível com granularidade de fonte e programa.

| Coluna | Descrição oficial | Uso no projeto |
|---|---|---|
| `data_assinatura_financiamento` | Data da contratação do financiamento | extrai o ano → eixo temporal |
| `vlr_financiamento` | Valor total das operações de crédito | somado por ano → série "FGTS" e "Fundo Social" do Gráfico 1, split por `txt_programa_fgts` |
| `txt_programa_fgts` | Apoio à Produção; Carta de Crédito Associativo; Carta de Crédito Individual; Classe Média; Faixa Estendida; **Fundo Social**; Pró-Cotista | `== "Fundo Social"` → série "Fundo Social"; demais valores válidos de MCMV → série "FGTS" |
| `txt_compatibilidade_faixa_renda` | Faixa 1; Faixa 2; Faixa 3; **FORA MCMV/CVA** | linhas com `FORA MCMV/CVA` são excluídas (não são MCMV) — premissa registrada em MEMORY do usuário, item 6 do prompt original |

### Filtro "não-MCMV" aplicado
Conforme observação prévia do usuário (contratos Pró-Cotista, Faixa Estendida e marcados "FORA MCMV/CVA" não são MCMV): o filtro efetivamente aplicado no script é `txt_compatibilidade_faixa_renda != "FORA MCMV/CVA"`. Os programas "Pró-Cotista" e "Faixa Estendida" foram mantidos como MCMV sempre que a faixa de renda é compatível (Faixa 1/2/3) — **esta é uma decisão de modelagem a validar**, não uma regra documentada explicitamente no dicionário oficial. Ver TODO em `scripts/process_financiamento_fonte_ano.py`.

## Convenção geral
- Ano de referência: extraído da data de assinatura/contratação de cada base (não da `data_referencia`, que é a data de geração do arquivo, não do contrato).
- Valores em R$ correntes (nominais), sem deflacionar — deflacionar é decisão para uma etapa posterior, a combinar.


## balanco_fgts.csv

- `ano`: encerramento em 31/12. A coluna 01/01/2022 reapresentada representa 2021.
- `rubrica`: conta patrimonial; inclui totais e componentes. Não somar indiscriminadamente.
- `valor_rs_milhares`: R$ milhares correntes, Controladora.
- `arquivo_fonte`: documento oficial transcrito.
- `pagina_fonte`: página física do PDF, base 1; vazia para o DOCX 2021.
- `localizador_fonte`: tabela/seção da fonte; tabelas 1–2 do DOCX para 2020.
- `tratamento`: publicado, reapresentado ou residual do ativo.

## ponte_caixa_fgts.csv

`ano`, `rubrica`, `valor_rs_milhares`, `arquivo_fonte`, `pagina_fonte`: mesmas definições de unidade e localização. Rubricas inicial/final são estoques; três atividades são fluxos mutuamente exclusivos. Inicial + atividades = final.

## deficit_fjp_total.csv

- `ano`: referência da pesquisa (2024), não ano de divulgação nem déficit de 2026.
- `territorio`: Brasil.
- `deficit_domicilios`: estoque estimado de domicílios em déficit (5.773.983).
- `percentual_domicilios`: percentual dos domicílios particulares ocupados (7,4; escala 0–100).
- `fonte_url`: divulgação oficial do Ministério das Cidades na Agência Gov.

As tabelas por renda e componente não foram recuperadas. Não há imputação, nem uso de percentuais de outra edição para repartir o total.
