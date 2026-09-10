"""
Monta outputs/graficos_reproduziveis.xlsx: cada gráfico do dashboard vira uma
aba com a tabela tidy + uma aba com o gráfico nativo do Excel (mesma paleta
categórica do dashboard), mais uma aba "Fontes" com a ficha de proveniência.

Roda depois de todo scripts/process_*.py.
"""
import json
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
OUT_PATH = ROOT / "outputs" / "graficos_reproduziveis.xlsx"

# mesma paleta categórica validada usada no dashboard/app.py
COR_FGTS = "2A78D6"
COR_OGU = "EB6834"
COR_FUNDO_SOCIAL = "1BAF7A"
ORDEM_FONTE = ["FGTS", "OGU", "Fundo Social"]
CORES_FONTE = {"FGTS": COR_FGTS, "OGU": COR_OGU, "Fundo Social": COR_FUNDO_SOCIAL}

GRAFICOS = ["financiamento_por_fonte_ano"]


def autosize(ws, df: pd.DataFrame) -> None:
    for i, col in enumerate(df.columns, start=1):
        largura = max(len(str(col)), df[col].astype(str).map(len).max()) + 2
        ws.column_dimensions[get_column_letter(i)].width = min(largura, 60)


def montar_aba_dados(wb: Workbook, nome: str, meta: dict) -> str:
    df = pd.read_csv(PROCESSED_DIR / f"{nome}.csv")
    tabela_wide = df.pivot(index="ano", columns="fonte", values="valor_total_financiado")
    tabela_wide = tabela_wide[[f for f in ORDEM_FONTE if f in tabela_wide.columns]]
    tabela_wide = (tabela_wide / 1e9).reset_index()
    tabela_wide.columns = ["ano"] + [f"{c} (R$ bi)" for c in tabela_wide.columns[1:]]

    aba_nome = f"Dados_{nome}"[:31]
    ws = wb.create_sheet(aba_nome)
    ws.append(list(tabela_wide.columns))
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for row in tabela_wide.itertuples(index=False):
        ws.append(list(row))
    autosize(ws, tabela_wide)
    ws.freeze_panes = "A2"
    return aba_nome


def montar_aba_grafico(wb: Workbook, nome: str, aba_dados: str, meta: dict) -> None:
    ws_dados = wb[aba_dados]
    n_linhas = ws_dados.max_row
    n_cols = ws_dados.max_column  # 1 (ano) + N fontes

    ws_graf = wb.create_sheet(f"Grafico_{nome}"[:31])
    ws_graf.sheet_view.showGridLines = False

    chart = BarChart()
    chart.type = "col"
    chart.grouping = "stacked"
    chart.overlap = 100
    chart.title = meta["titulo"]
    chart.y_axis.title = "R$ bilhões (valores correntes)"
    chart.x_axis.title = None
    chart.height = 12
    chart.width = 26

    data = Reference(ws_dados, min_col=2, max_col=n_cols, min_row=1, max_row=n_linhas)
    cats = Reference(ws_dados, min_col=1, min_row=2, max_row=n_linhas)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)

    # cores por série, mesma paleta do dashboard
    colunas_fonte = [c.value.split(" (")[0] for c in ws_dados[1][1:]]
    for serie, nome_fonte in zip(chart.series, colunas_fonte):
        cor = CORES_FONTE.get(nome_fonte)
        if cor:
            serie.graphicalProperties.solidFill = cor
            serie.graphicalProperties.line.noFill = True

    ws_graf.add_chart(chart, "B2")


def montar_aba_fontes(wb: Workbook, metas: list) -> None:
    ws = wb.create_sheet("Fontes")
    ws.append(["Gráfico", "Organização", "Base", "Nível", "URL", "Data de acesso", "Script", "Tabela"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for meta in metas:
        for base in meta["bases"]:
            ws.append([
                meta["titulo"],
                meta["organizacao"],
                base["nome"],
                base["nivel"],
                base["url"],
                meta["data_acesso"],
                meta["script"],
                meta["tabela"],
            ])
    for i in range(1, 9):
        ws.column_dimensions[get_column_letter(i)].width = 28
    ws.freeze_panes = "A2"


def main():
    wb = Workbook()
    wb.remove(wb.active)  # remove a aba default "Sheet"

    metas = []
    for nome in GRAFICOS:
        with open(PROCESSED_DIR / f"{nome}.meta.json", encoding="utf-8") as f:
            meta = json.load(f)
        metas.append(meta)
        aba_dados = montar_aba_dados(wb, nome, meta)
        montar_aba_grafico(wb, nome, aba_dados, meta)

    montar_aba_fontes(wb, metas)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT_PATH)
    print(f"Salvo em {OUT_PATH}")


if __name__ == "__main__":
    main()
