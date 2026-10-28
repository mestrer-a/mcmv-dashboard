"""Hipótese FAR compartilhada pelo mapa, figuras e simulador."""


def far_subsidy(value, exempt=0., loss=0., rate=.06):
    if value < 0 or not 0 <= exempt <= 1 or not 0 <= loss <= 1 or rate < 0:
        raise ValueError('Parâmetros fora do domínio')
    receipts = sum(.1 * value / 60 / (1 + rate) ** (m / 12) for m in range(1, 61))
    return value - (1 - exempt) * (1 - loss) * receipts
