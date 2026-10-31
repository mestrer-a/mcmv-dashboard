import unittest,json
from pathlib import Path
import numpy as np
import pandas as pd
D=Path(__file__).resolve().parents[1]/'data/processed'
class RevisionTests(unittest.TestCase):
 def test_accounting_and_allocation(self):
  u=pd.read_csv(D/'revisao_custo_unitario.csv');c=pd.read_csv(D/'revisao_custo_deficit.csv')
  np.testing.assert_allclose(u.total,u.explicito+np.maximum(0,u.beneficio_juros-u.equilibrio))
  np.testing.assert_allclose(u.explicito,u.complemento+u.equilibrio)
  np.testing.assert_allclose(c.total,c.far_custo+c.explicito+c.implicito)
  self.assertAlmostEqual(c[c.recorte=='Total'].domicilios.sum(),5773983)
  self.assertAlmostEqual(c[c.recorte!='Total'].domicilios.sum(),2186206)
  self.assertTrue((c.principal>0).all())
 def test_sac_present_value_identity(self):
  p=130000;n=360;j=.045/12;k=1.13**(1/12)-1;t=np.arange(1,n+1);b=p*(1-(t-1)/n)
  self.assertAlmostEqual(float(np.sum(b*(k-j)/(1+k)**t)),p-float(np.sum((p/n+b*j)/(1+k)**t)),places=6)
 def test_dfc_reconciliation(self):
  d=pd.read_csv(D/'sim_dfc_reconciliacao.csv')
  np.testing.assert_allclose(d.cash_end-d.cash_start,d.op_total+d.inv_total+d.deposits+d.withdrawals-d.pis_transfer)
  np.testing.assert_allclose(d.maintenance,d.deposits+d.withdrawals+d.op_total+d.bond_interest+d.other_inv)
