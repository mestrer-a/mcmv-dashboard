import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dashboard'))
from inicio import far_subsidy
from streamlit.testing.v1 import AppTest
class HomeTests(unittest.TestCase):
 def test_far(self):
  v=174345.19176323107
  self.assertAlmostEqual(far_subsidy(v),159257.41070965742)
  self.assertAlmostEqual(far_subsidy(v,rate=0),.9*v)
  self.assertEqual(far_subsidy(v,exempt=1),v)
  self.assertEqual(far_subsidy(v,loss=1),v)
  self.assertAlmostEqual(v-far_subsidy(v,.5,.2),.4*(v-far_subsidy(v)))
 def test_home(self):
  a=AppTest.from_file(str(ROOT/'dashboard/app.py'),default_timeout=40).run()
  self.assertFalse(a.exception,list(a.exception))
  self.assertEqual(len(a.get('plotly_chart')),5)
  a.slider(key='home_exempt').set_value(100).run()
  self.assertIn('R$ 174.345,19',[m.value for m in a.metric])
  a.button(key='home_go_6').click().run()
  self.assertEqual(a.radio(key='nav_page').value,6)
  self.assertFalse(a.exception,list(a.exception))
  a.radio(key='nav_page').set_value(0).run()
  self.assertFalse(a.exception,list(a.exception))
if __name__=='__main__':unittest.main()
