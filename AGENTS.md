# Continuidade da dissertação MCMV

A cada nova versão da dissertação ou apresentação, conferir todos os gráficos e tabelas utilizados. Atualizar suas reproduções no dashboard e avaliar se a árvore precisa acompanhar mudanças no argumento, parâmetros ou resultados.

Inventário de referência: `docs/graficos_dissertacao.md`; catálogo e reproduções
fixas: `dashboard/figuras_dissertacao.py`. Atualizar ambos quando mudar a versão.

Antes de declarar uma figura concluída, conferir seus valores e a renderização
no navegador. Distinguir o que a fonte efetivamente calcula de hipóteses
acrescentadas pela dissertação. Na Figura 1A, a revisão de 30/10/2026 usa média DI nominal até 60 meses
(pregão de 29/10/2026) e parcelas nominais fixas, sem reajuste/TR ou carência.
A hipótese original de parcelas reais e 6% reais fica preservada e identificada
na memória de cálculo. Nunca aplicar taxa nominal a parcelas reais sem conversão.
A contribuição uniforme de 10% é hipótese própria; a SECAP descreve participação de até 10% e contabiliza
os aportes FAR/FDS integralmente como subsídio na sua análise econômica.

A página inicial conecta o mapa visual (`dashboard/assets/mapa_dissertacao.html`)
às evidências e ao simulador em `dashboard/inicio.py`.

Ao receber nova versão da dissertação, avaliar mudanças na pergunta de pesquisa,
literatura, hipóteses, parâmetros, resultados e ordem da apresentação. Atualizar
a árvore quando o argumento mudar. Conferir a coerência entre texto, mapa,
gráficos e bases; registrar a versão de referência. Priorizar desenhos, números
e gráficos com unidade, período e fonte.

Preservar as demais páginas. Distinguir dados observados de cenários. Não tratar
principal reembolsável como subsídio. Perdas entram uma vez nos recebimentos.
Não duplicar equalização e diferencial de juros. FAR e FGTS têm fluxos distintos.
Custo em valor presente não substitui liquidez anual ou mensal.

Verificação: testes de fórmula, controles e navegação da página inicial.
Comando: `python -m unittest discover -s tests -v`.

DI é referência de oportunidade do cenário, não remuneração contratual do FAR/FDS.
FDS exige custo e recebimentos próprios; estimativa específica segue pendente de
renda, isenções e fluxos por safra. OGU é fonte: não somar novamente FAR/FDS.
