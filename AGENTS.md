# Continuidade da dissertação MCMV

A cada nova versão da dissertação ou apresentação, conferir todos os gráficos e tabelas utilizados. Atualizar suas reproduções no dashboard e avaliar se a árvore precisa acompanhar mudanças no argumento, parâmetros ou resultados.

Inventário de referência: `docs/graficos_dissertacao.md`; catálogo e reproduções
fixas: `dashboard/figuras_dissertacao.py`. Atualizar ambos quando mudar a versão.

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
