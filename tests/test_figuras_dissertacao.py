"""Confronto com valores do documento e acesso a cada figura na aplicação."""
import json
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dashboard'))
from figuras_dissertacao import FIGURES, figure_data, build_figure, source_links
from far import far_subsidy


class DissertationDataTests(unittest.TestCase):
    def test_inventory_covers_every_document_caption(self):
        inventory=json.loads((ROOT/'docs/inventario_figuras.json').read_text())
        self.assertEqual(list(FIGURES),[f['numero'] for f in inventory['figuras']])
        self.assertEqual(len(FIGURES),15)
        for n,s in FIGURES.items():
            with self.subTest(figure=n):
                self.assertFalse(figure_data(n).empty)
                self.assertTrue(build_figure(n).data)
                self.assertTrue(source_links(n))
                for field in ('title','period','unit','kind','formula','assumptions'):
                    self.assertTrue(s[field])

    def test_far_patch_scenarios_match_document_and_model(self):
        d=figure_data('1A')
        np.testing.assert_allclose(d['Subsídio líquido (R$)'],
            [159257.41070965742,166801.30123644424,168310.0793418016,174345.19176323107])
        np.testing.assert_allclose(d['Valor bruto (R$)']-d['Recebimentos em VP (R$)'],d['Subsídio líquido (R$)'])
        v=d['Valor bruto (R$)'].iloc[0]
        self.assertAlmostEqual(v-far_subsidy(v,.5,.2),.4*(v-far_subsidy(v)))
        self.assertEqual(far_subsidy(v,1,.2),v)

    def test_administrative_figures_match_document(self):
        g=figure_data('1').set_index('Faixa')
        np.testing.assert_allclose(g['Subsídio registrado (R$ por contrato)'],[44045.943968,8177.234924,0,0],rtol=1e-9)
        d=figure_data('3')
        self.assertEqual(d.groupby('ano').contratos.sum().to_dict(),
            {2023:452592,2024:586810,2025:659127,2026:396869})
        d=figure_data('4')
        self.assertEqual(set(d.ano),{2023,2024,2025,2026})
        self.assertAlmostEqual(d.financiamento.sum()/d.financiamento_observado.sum(),
            (d['R$ mil por operação']*d.financiamento_observado).sum()/d.financiamento_observado.sum()*1000)
        d=figure_data('2')
        np.testing.assert_allclose(d['Mínimo (% a.a.)'],[4,4.75,7.66,10])
        np.testing.assert_allclose(d['Máximo (% a.a.)'],[5.25,7,8.16,10])
        d=figure_data('5')
        self.assertEqual(set(d.ano),set(range(2009,2027)))
        self.assertAlmostEqual(d.query('ano==2025 and fonte=="FGTS"').valor_total_financiado.sum()/1e9,104.5,delta=.1)

    def test_fjp_components_and_methodology_breaks(self):
        d=figure_data('9')
        self.assertEqual(d.groupby('ano').deficit_domicilios.sum().to_dict(),{2022:6215313,2024:5773983})
        self.assertEqual(d.query('ano==2024').deficit_domicilios.tolist(),[1156834,1029372,3587777])
        fig=build_figure('8')
        for trace in fig.data:
            years=[x for x,y in zip(trace.x,trace.y) if y is not None]
            self.assertNotIn(2020,years)
            self.assertNotIn(2021,years)
            if any(y>=2022 for y in years) or years==[2010]:
                self.assertEqual(trace.mode,'markers')
        annual=next(t for t in fig.data if t.name.startswith('Pnad anual'))
        self.assertIsNone(annual.y[list(annual.x).index(2010)])

    def test_fgts_figures_reconcile_and_preserve_negative_spread(self):
        d=figure_data('6').pivot(index='ano',columns='Medida',values='R$ bilhões correntes')
        self.assertAlmostEqual(d.loc[2020,'Arrecadação']-d.loc[2020,'Saques'],-13.05,delta=.01)
        d=figure_data('7')
        self.assertAlmostEqual(d.query('ano==2025 and rubrica=="Caixa e equivalentes"')['R$ bilhões correntes'].iloc[0],33.466156)
        d=figure_data('10').set_index('ano')
        self.assertAlmostEqual(d.loc[2025,'Diferencial bruto (R$ bi)'],42.14,delta=.01)
        self.assertAlmostEqual(d.loc[2021,'Diferencial bruto (R$ bi)'],-2.22,delta=.01)
        self.assertEqual(len(build_figure('10').data),3)
        self.assertEqual(build_figure('10').data[2].xaxis,'x2')

    def test_cash_paths_support_and_annual_scale_match_document(self):
        d=figure_data('11')
        np.testing.assert_allclose(d.maintenance_real_bi,[15.72340808375,-3.7642808725,-7.580399209])
        np.testing.assert_allclose(d.delta_real_bi,(d.cash_end-d.cash_start)*d.factor/1e6)
        t=figure_data('12');s=figure_data('13')
        self.assertEqual(t.cenario.nunique(),7)
        self.assertEqual(set(t.ano),set(range(2025,2041)))
        np.testing.assert_allclose(t.saldo_indicativo_bi,33.466156+(t.ano-2025)*t.fluxo_anual_bi)
        np.testing.assert_allclose(s.aporte_anual_preserva_caixa_bi,np.maximum(0,-s.fluxo_anual_bi))
        combined=s.set_index('cenario').loc['Choques combinados']
        self.assertAlmostEqual(combined.aporte_anual_preserva_caixa_bi,21.71,delta=.01)
        d=figure_data('14').set_index('recorte')
        np.testing.assert_allclose(d.loc['Total',['far_anual_bi','credito_anual_bi','subsidio_anual_bi']].astype(float),[50.33,37.70,13.47],atol=.01)
        np.testing.assert_allclose(d.loc['Sem ônus com aluguel',['far_anual_bi','credito_anual_bi','subsidio_anual_bi']].astype(float),[19.06,14.27,5.10],atol=.01)
        p=json.loads((ROOT/'data/processed/sim_parametros.json').read_text())
        self.assertAlmostEqual(p['subsidio_faixa1_rs'],46649.58,delta=.01)
        self.assertAlmostEqual(5773983*.5*far_subsidy(p['far_unitario_rs'])/1e9,459.77,delta=.01)


class DissertationNavigationTests(unittest.TestCase):
    def test_every_index_entry_opens_its_figure_with_download(self):
        app=AppTest.from_file(str(ROOT/'dashboard/app.py'),default_timeout=60).run()
        for n,s in FIGURES.items():
            app.radio(key='nav_page').set_value(0).run()
            with self.subTest(figure=n):
                app.button(key=f'figure_open_{n}').click().run()
                self.assertFalse(app.exception,list(app.exception))
                self.assertEqual(app.radio(key='nav_page').value,s['page'])
                self.assertEqual(app.selectbox(key=f'dissertation_selection_{s["page"]}').value,n)
                charts=app.get('plotly_chart')
                self.assertTrue(any(c.proto.id.endswith(f'-dissertation_figure_{n}') for c in charts))
                self.assertTrue(any(b.proto.id.endswith(f'-dissertation_figure_{n}_csv') for b in app.get('download_button')))
                app.radio(key='nav_page').set_value(0).run()
                self.assertFalse(app.exception,list(app.exception))

    def test_other_navigation_pages_remain_available(self):
        app=AppTest.from_file(str(ROOT/'dashboard/app.py'),default_timeout=60).run()
        for page in (3,5):
            app.radio(key='nav_page').set_value(page).run()
            self.assertFalse(app.exception,list(app.exception))
            self.assertEqual(app.radio(key='nav_page').value,page)


if __name__=='__main__':
    unittest.main()
