"""Figura estática da dissertação, a partir do mesmo CSV do dashboard.

Requer matplotlib. Ex.: python scripts/build_figura_balanco.py --output figura.png
"""
import argparse
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

parser=argparse.ArgumentParser()
parser.add_argument('--output',default='outputs/fgts_stocks.png')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
with (root/'data/processed/balanco_fgts.csv').open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(8.4,3.8))
for rub,color in [('Caixa e equivalentes','#2378A8'),('Patrimônio líquido','#DD754B')]:
    t=[r for r in rows if r['rubrica']==rub]
    ax.plot([int(r['ano']) for r in t],[int(r['valor_rs_milhares'])/1e6 for r in t],marker='o',label=rub,color=color,lw=2.2)
ax.set_ylabel('R$ bilhões correntes');ax.set_xticks(range(2020,2026))
ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.2)
ax.set_ylim(0,145);ax.legend(frameon=False,loc='upper left',ncol=2)
fig.tight_layout();path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(path,dpi=220);plt.close(fig)
