"""Cenário FAR: taxa única nominal e parcelas nominais sem reajuste.

O valor-base pode ser normalizado em preços de dez./2025: multiplicar todos
os fluxos nominais e o VP pelo mesmo deflator não altera a proporção de apoio.
Isso não torna as parcelas futuras constantes em poder de compra.
"""
import csv
from pathlib import Path
from statistics import mean

CURVE_PATH = Path(__file__).resolve().parents[1]/'data/processed/di_vertices_20261029.csv'
with CURVE_PATH.open(encoding='utf-8') as _file:
    DI_VERTICES = tuple(csv.DictReader(_file))
SELECTED_VERTICES = tuple(r for r in DI_VERTICES if r['selecionado_60m']=='True')
DISCOUNT_RATE = mean(float(r['taxa_ajuste_aa']) for r in SELECTED_VERTICES)/100
DISCOUNT_DATE = '29/10/2026'


def far_subsidy(value, exempt=0., loss=0., rate=DISCOUNT_RATE):
    """10% de V em 60 pagamentos fixos, fim de mês; perda só nos pagantes.

    Taxa anual efetiva convertida por m/12, sem casamento com cada vértice.
    Chamar rate=.06 reproduz numericamente a antiga hipótese real da dissertação,
    que pressupunha parcelas reais constantes e tem interpretação distinta.
    """
    if value < 0 or not 0 <= exempt <= 1 or not 0 <= loss <= 1 or rate < 0:
        raise ValueError('Parâmetros fora do domínio')
    receipts = sum(.1 * value / 60 / (1 + rate) ** (m / 12) for m in range(1, 61))
    return value - (1 - exempt) * (1 - loss) * receipts
