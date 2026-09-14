import json
from pathlib import Path
import pandas as pd
out=Path(__file__).resolve().parents[1]/'data/processed'
u='https://www.gov.br/cidades/pt-br/acesso-a-informacao/institucional/base-juridica/resolucoes/fgts/Res_CCFGTS_2025_1133.pdf'
v='https://www.gov.br/trabalho-e-emprego/pt-br/noticias-e-conteudo/2026/setembro/conselho-suplementa-r-500-milhoes-no-orcamento-do-fgts-para-subsidio-habitacional'
d=pd.DataFrame({'ano':[2026]*3,'area':['Habitação','Saneamento básico','Infraestrutura urbana'],'valor_rs_milhares':[144500000,8000000,8000000]})
d.to_csv(out/'orcamento_operacional_2026.csv',index=False)
m={'id':'orcamento_operacional_2026','titulo':'Orçamento operacional inicial do FGTS em 2026','data_acesso':'2026-09-13','bases':[{'nome':'CCFGTS Resolução 1.133/2025, anexo IV, página 5 do PDF', 'url':u},{'nome':'MTE: suplementação dos descontos em 10/09/2026','url':v}],'premissas':['Orçamento inicial aprovado em 2025, não consolidação de reprogramações posteriores de 2026.','Contratação planejada, não execução, caixa disponível ou custo econômico.','Anexo IV, unidade R$ mil: 144.500.000 + 8.000.000 + 8.000.000 = 160.500.000.','Descontos separados do total de contratações; 12,5 bi iniciais e 13,0 bi após suplementação divulgada em setembro.']}
m.update(script='scripts/process_orcamento_operacional_2026.py',tabela='data/processed/orcamento_operacional_2026.csv',metrica='Orçamento inicial de contratação por área, em R$ mil',localizador='Anexo IV, página 5 do PDF; coluna 2026')
(out/'orcamento_operacional_2026.meta.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
