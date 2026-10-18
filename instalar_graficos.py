"""Integra o painel de juros ao dashboard sem modificar os gráficos existentes.

Este utilitário é idempotente. O repositório publicado já contém a integração;
o arquivo é mantido apenas para reproduzir a instalação preparada no ZIP.
"""
from pathlib import Path

root = Path(__file__).resolve().parent
app = root / 'dashboard' / 'app.py'
module = root / 'dashboard' / 'juros.py'

if not app.exists() or not module.exists():
    raise SystemExit('Arquivos do dashboard não encontrados.')

source = app.read_text(encoding='utf-8')
if 'from juros import render_juros_2026' not in source:
    source = source.replace(
        'from additions import ',
        'from juros import render_juros_2026\nfrom additions import ',
        1,
    )
if '        render_juros_2026()' not in source:
    target = '        far_comparison()'
    if target not in source:
        raise SystemExit('Ponto de integração não encontrado; nenhuma mudança foi feita.')
    source = source.replace(target, '        render_juros_2026()\n' + target, 1)

app.write_text(source, encoding='utf-8')
print('Integração dos gráficos de juros conferida.')
