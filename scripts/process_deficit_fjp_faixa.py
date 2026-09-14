"""
Processa o déficit habitacional por faixa de renda do MCMV e por componente,
edição de referência 2022 (PnadC 2022), da Fundação João Pinheiro.

Fonte primária (transcrição manual, com citação de página):
  FUNDAÇÃO JOÃO PINHEIRO. Déficit Habitacional no Brasil 2022.
  Belo Horizonte: FJP, 2023. 72 p.
  Repositório: https://repositorio.fjp.mg.gov.br/handle/123456789/4262
  PDF: https://repositorio.fjp.mg.gov.br/bitstreams/cc248796-b48a-404f-a4b9-ea931f898604/download
  - Tabela 4 (valores absolutos), p. 30-31
  - Tabela 5 (composição % por faixa), p. 31-32
  - Gráfico 2 (composição relativa por faixa), p. 29

Regra do projeto: nada solto. Todo número aqui foi conferido contra o PDF
oficial da FJP. O servidor da FJP bloqueia leitura automatizada, então a
transcrição é manual; este script é o registro auditável dela.

Faixas de renda = faixas do MCMV em R$ (Lei nº 14.620/2023, art. 5º, I),
conforme definido pela própria FJP no relatório (p. 28-29):
  Faixa 1:        renda familiar mensal até R$ 2.640,00
  Faixa 2:        de R$ 2.640,01 até R$ 4.400,00
  Faixa 3:        de R$ 4.400,01 até R$ 8.000,00
  Acima Faixa 3:  acima de R$ 8.000,00
O crosswalk renda -> faixa é feito pela FJP; NÃO equiparar aos códigos de
faixa das bases de contratos do MCMV.
"""

import csv
import json
import os

ANO_REFERENCIA = 2022
DATA_ACESSO = "2026-09-13"

# ---------------------------------------------------------------------------
# Tabela 4 - Déficit habitacional, por faixa de renda do MCMV, segundo
# regiões geográficas - Brasil - 2022 (valores absolutos, domicílios).
# Ordem das colunas: [Faixa 1, Faixa 2, Faixa 3, Acima da Faixa 3, Total].
# p. 30 (Norte a Centro-Oeste/precários-coabitação) e p. 31 (Centro-Oeste
# ônus-déficit, Brasil, Total das RM, Demais áreas).
# ---------------------------------------------------------------------------
FAIXAS = ["faixa_1", "faixa_2", "faixa_3", "acima_faixa_3", "total"]

# componente: "precaria" | "coabitacao" | "onus_aluguel" | "deficit_total"
TAB4 = {
    "Norte": {
        "precaria":      [295896, 23781, 9153, 2432, 331262],
        "coabitacao":    [97562, 72160, 58706, 28973, 257402],
        "onus_aluguel":  [167438, 17227, 0, 0, 184665],
        "deficit_total": [560896, 113168, 67860, 31405, 773329],
    },
    "Nordeste": {
        "precaria":      [660743, 28158, 14028, 328, 703256],
        "coabitacao":    [148955, 114495, 86143, 16860, 366454],
        "onus_aluguel":  [657418, 33904, 0, 0, 691322],
        "deficit_total": [1467116, 176557, 100171, 17188, 1761032],
    },
    "Sudeste": {
        "precaria":      [299515, 18775, 12534, 6088, 336911],
        "coabitacao":    [103633, 105263, 166832, 108604, 484332],
        "onus_aluguel":  [1330520, 291878, 0, 0, 1622398],
        "deficit_total": [1733668, 415915, 179366, 114692, 2443642],
    },
    "Sul": {
        "precaria":      [126954, 32348, 26777, 7285, 193364],
        "coabitacao":    [10741, 20197, 39269, 27575, 97782],
        "onus_aluguel":  [348773, 97707, 0, 0, 446481],
        "deficit_total": [486469, 150252, 66045, 34860, 737626],
    },
    "Centro-Oeste": {
        "precaria":      [99184, 9080, 8265, 1331, 117860],
        "coabitacao":    [23492, 15539, 27883, 16996, 83910],
        "onus_aluguel":  [259222, 38693, 0, 0, 297915],
        "deficit_total": [381897, 63312, 36148, 18327, 499685],
    },
    "Brasil": {
        "precaria":      [1482292, 112141, 70757, 17464, 1682654],
        "coabitacao":    [384384, 327654, 378833, 199008, 1289879],
        "onus_aluguel":  [2763371, 479409, 0, 0, 3242780],
        "deficit_total": [4630046, 919205, 449590, 216472, 6215313],
    },
    "Total das RM": {
        "precaria":      [289880, 24201, 19447, 8345, 341873],
        "coabitacao":    [129229, 127085, 170957, 103949, 531221],
        "onus_aluguel":  [1190988, 246018, 0, 0, 1437006],
        "deficit_total": [1610097, 397304, 190404, 112294, 2310100],
    },
    "Demais áreas": {
        "precaria":      [1192412, 87940, 51310, 9119, 1340781],
        "coabitacao":    [255154, 200569, 207876, 95058, 758658],
        "onus_aluguel":  [1572383, 233392, 0, 0, 1805774],
        "deficit_total": [3019949, 521901, 259186, 104177, 3905213],
    },
}

# ---------------------------------------------------------------------------
# Verificações de consistência (nada solto).
# ---------------------------------------------------------------------------
def _check():
    b = TAB4["Brasil"]["deficit_total"]
    assert b[4] == 6215313, "Total Brasil difere do relatório."
    # Brasil = Total das RM + Demais áreas, célula a célula. A ponderação
    # amostral da PnadC faz os totais impressos divergirem em +-alguns
    # domicílios; tolerância de 5 evita quebrar em arredondamento legítimo,
    # mas qualquer divergência é impressa para auditoria.
    TOL = 5
    maior = 0
    for comp in ["precaria", "coabitacao", "onus_aluguel", "deficit_total"]:
        for i in range(5):
            soma = TAB4["Total das RM"][comp][i] + TAB4["Demais áreas"][comp][i]
            diff = abs(soma - TAB4["Brasil"][comp][i])
            maior = max(maior, diff)
            assert diff <= TOL, (
                f"Brasil != RM+Demais em {comp}[{i}]: {soma} vs "
                f"{TAB4['Brasil'][comp][i]} (diff {diff} > {TOL})"
            )
    print(f"Verificações OK: total Brasil = 6.215.313; identidade RM + Demais "
          f"áreas dentro da tolerância (maior divergência: {maior} domicílios).")


def main():
    _check()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(here, "data", "processed")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "deficit_fjp_faixa_componente.csv")

    rows = []
    for territorio, comps in TAB4.items():
        for componente, valores in comps.items():
            for faixa, valor in zip(FAIXAS, valores):
                rows.append({
                    "ano_referencia": ANO_REFERENCIA,
                    "territorio": territorio,
                    "componente": componente,
                    "faixa": faixa,
                    "deficit_domicilios": valor,
                })

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "ano_referencia", "territorio", "componente", "faixa",
            "deficit_domicilios",
        ])
        w.writeheader()
        w.writerows(rows)
    print(f"Escrito {csv_path} ({len(rows)} linhas)")

    # Metadados de proveniência, no padrão do repo.
    meta = {
        "id": "deficit_fjp_faixa_componente",
        "titulo": "Déficit habitacional por faixa de renda do MCMV e por componente, referência 2022",
        "organizacao": "Fundação João Pinheiro (FJP)",
        "portal_catalogo": "https://repositorio.fjp.mg.gov.br/handle/123456789/4262",
        "data_acesso": DATA_ACESSO,
        "bases": [
            {
                "nome": "FUNDAÇÃO JOÃO PINHEIRO. Déficit Habitacional no Brasil 2022. Belo Horizonte: FJP, 2023. 72 p.",
                "url": "https://repositorio.fjp.mg.gov.br/bitstreams/cc248796-b48a-404f-a4b9-ea931f898604/download",
                "tabelas": "Tabela 4 (absoluto, p. 30-31); Tabela 5 (composição %, p. 31-32); Gráfico 2 (p. 29)",
            }
        ],
        "por_que_essa_versao": (
            "Edição de referência 2022 (PnadC 2022) é a publicação completa mais recente "
            "da FJP com abertura do déficit por faixa de renda do MCMV e por componente. "
            "O total de referência 2024 (5.773.983) circulou apenas como manchete via "
            "Ministério das Cidades (abril/2026), sem relatório com as tabelas por renda e "
            "componente. Para o exercício de custo, usa-se a edição 2022 de forma consistente "
            "(total e abertura da mesma fonte); o total de 2024 pode ser citado como contexto."
        ),
        "script": "scripts/process_deficit_fjp_faixa.py",
        "tabela": "data/processed/deficit_fjp_faixa_componente.csv",
        "metrica": (
            "Domicílios em déficit habitacional, por faixa de renda do MCMV (R$) e por "
            "componente (habitação precária, coabitação, ônus excessivo com aluguel urbano), "
            "por território."
        ),
        "premissas": [
            "Faixas em R$ do MCMV (Lei 14.620/2023, art. 5, I), conforme a própria FJP: "
            "Faixa 1 ate R$2.640; Faixa 2 ate R$4.400; Faixa 3 ate R$8.000; Acima acima de R$8.000.",
            "O crosswalk renda -> faixa e feito pela FJP. NAO equiparar aos codigos de faixa "
            "das bases de contratos do MCMV, que tem regras e tetos proprios que mudam no tempo.",
            "Onus excessivo com aluguel so e definido para renda ate 3 SM; por isso e zero nas "
            "Faixas 3 e Acima da Faixa 3.",
            "Totais impressos podem divergir da soma dos componentes em +-1 a 5 domicilios por "
            "conta da ponderacao amostral da PnadC. Valores transcritos como no original.",
            "Quebra metodologica: metodologia atual (revisao ~2016, migracao para PnadC + "
            "CadUnico) nao e comparavel ponta a ponta com as series antigas da FJP.",
            "Deficit e dado de ENTRADA (FJP). O trabalho nao recalcula nem prorrateia a "
            "distribuicao de 2022 sobre totais de outros anos.",
            "Uma unidade em deficit nao equivale a uma unidade a construir: ~52% do deficit "
            "nacional e onus excessivo com aluguel (nao demanda necessariamente nova unidade).",
        ],
    }
    meta_path = os.path.join(out_dir, "deficit_fjp_faixa_componente.meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Escrito {meta_path}")

    # Resumo Brasil para conferência rápida.
    b = TAB4["Brasil"]["deficit_total"]
    tot = b[4]
    print("\nResumo Brasil (déficit por faixa):")
    for faixa, v in zip(FAIXAS[:-1], b[:-1]):
        print(f"  {faixa:14s} {v:>10,} ({v / tot:6.1%})")
    onus = TAB4["Brasil"]["onus_aluguel"][4]
    print(f"  {'TOTAL':14s} {tot:>10,}")
    print(f"  ônus de aluguel = {onus:,} ({onus / tot:.1%} do déficit nacional)")


if __name__ == "__main__":
    main()
