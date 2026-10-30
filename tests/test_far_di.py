"""Referência de mercado, domínio nominal e preservação da hipótese documental."""
import csv
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dashboard'))
from far import DISCOUNT_RATE,far_subsidy
from far_historico import summary_data,NET,RET
from streamlit.testing.v1 import AppTest


class DiscountTests(unittest.TestCase):
    def test_curve_selection_and_unweighted_mean(self):
        with (ROOT/'data/processed/di_vertices_20261029.csv').open() as f:
            rows=list(csv.DictReader(f))
        selected=[r for r in rows if r['selecionado_60m']=='True']
        self.assertEqual(len(rows),44)
        self.assertEqual(len(selected),34)
        self.assertEqual(selected[0]['contrato'],'DI1X26')
        self.assertEqual(selected[-1]['contrato'],'DI1V31')
        self.assertTrue(all(('2026-10'<r['vencimento_mes']<='2031-10') == (r['selecionado_60m']=='True') for r in rows))
        self.assertAlmostEqual(DISCOUNT_RATE,.14530882352941177)
        self.assertAlmostEqual(DISCOUNT_RATE*100,sum(float(r['taxa_ajuste_aa']) for r in selected)/34)

    def test_nominal_annuity_and_legacy_are_distinct(self):
        value=174345.19176323107
        monthly=(1+DISCOUNT_RATE)**(1/12)-1
        pv=value*.1/60*(1-(1+monthly)**-60)/monthly
        self.assertAlmostEqual(pv,12587.564602385402)
        self.assertAlmostEqual(value-far_subsidy(value),pv)
        self.assertAlmostEqual(far_subsidy(value,rate=.06),159257.41070965742)
        self.assertAlmostEqual(value-far_subsidy(value,.5,.2),.4*pv)
        d=summary_data().iloc[0]
        self.assertEqual(d['Reajuste anual (%)'],0)
        self.assertAlmostEqual(d[RET],pv)
        self.assertAlmostEqual(d[NET],161757.62716084567)

    def test_simulator_uses_exact_reference_and_nominal_label(self):
        app=AppTest.from_file(str(ROOT/'dashboard/app.py'),default_timeout=60).run()
        self.assertFalse(app.exception,list(app.exception))
        self.assertAlmostEqual(app.number_input(key='home_rate').value,DISCOUNT_RATE*100)
        self.assertIn('nominal',app.number_input(key='home_rate').label)
        self.assertIn('R$ 161.757,63',[m.value for m in app.metric])
        app.number_input(key='home_rate').set_value(0.).run()
        self.assertIn('R$ 156.910,67',[m.value for m in app.metric])
        self.assertFalse(app.exception,list(app.exception))


if __name__=='__main__':unittest.main()
