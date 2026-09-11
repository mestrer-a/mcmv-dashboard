"""Reconciliação das agregações e smoke test das páginas e controles."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))
from exploracao import stress_grid


def main():
    d = pd.read_csv(ROOT / "data/processed/exploracao_contratos.csv")
    original = pd.read_csv(ROOT / "data/processed/financiamento_por_fonte_ano.csv")
    comparison = d.groupby(["ano", "fonte"]).financiamento.sum().to_frame().join(
        original[original.fonte != "OGU"].set_index(["ano", "fonte"]))
    assert comparison.valor_total_financiado.notna().all()
    assert np.allclose(comparison.financiamento, comparison.valor_total_financiado, rtol=1e-10, atol=.1)
    assert (d.contratos_subsidio_observado <= d.contratos).all()
    assert (d.contratos_com_subsidio <= d.contratos_subsidio_observado).all()
    assert np.allclose(d.subsidio_total, d.subsidio_fgts+d.subsidio_ogu)
    assert not d.duplicated(["ano", "fonte", "faixa_codigo"]).any()
    g = stress_grid(200e6, 180e6)
    assert g.iloc[0].saldo_bi == 20
    assert g.loc[(g.queda_arrecadacao == .1) & (g.alta_saques == 0), "saldo_bi"].iloc[0] == 0
    app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=30).run()
    assert not app.exception, app.exception
    for page, expected in [(1, 8), (2, 6), (3, 4)]:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, app.exception
        app.radio(key=f"leitura_{page-1}").set_value("Explorações e hipóteses").run()
        assert not app.exception, app.exception
        count = len(app.get("vega_lite_chart")) + len(app.get("arrow_vega_lite_chart"))
        assert count == expected, (page, count)
        if page == 1:
            app.checkbox(key="fontes_parcial").check().run()
            app.checkbox(key="contratos_parcial").check().run()
            app.multiselect(key="credito_fontes").set_value([]).run()
            assert not app.exception
            app.multiselect(key="credito_fontes").set_value(["Fundo Social"]).run()
            assert not app.exception
            app.select_slider(key="contratos_periodo").set_value((2009, 2010)).run()
            assert not app.exception
        elif page == 2:
            app.select_slider(key="fgts_periodo").set_value((2025, 2025)).run()
            assert not app.exception
        else:
            app.slider(key="choque_formalizacao").set_value(-10.0).run()
            app.slider(key="choque_salario").set_value(20).run()
            assert not app.exception
    for page in [4, 5, 0]:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception
    print("OK: reconciliação do financiamento, integridade dos subsídios, 18 gráficos, abas e filtros extremos.")


if __name__ == "__main__":
    main()
