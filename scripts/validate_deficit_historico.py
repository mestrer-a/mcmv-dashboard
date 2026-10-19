"""Verifica anos, edições, lacunas e reconciliação dos totais publicados."""
from pathlib import Path
import hashlib
import sys
from unittest.mock import patch
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'dashboard'))
from deficit_historico import history_figure
from ui import plot


def main():
    d=pd.read_csv(ROOT/'data/processed/deficit_fjp_historico.csv')
    expected={1991:5374380,2000:7222645,2004:7804619,2005:7902699,2006:7934719,
              2007:5855375,2008:5437709,2009:5897976,2010:6940691,2011:5581968,
              2012:5430562,2013:5846040,2014:6068061,2015:6355743,2016:5768482,
              2017:6068566,2018:5973218,2019:5964993,2022:6215313,2023:5977317,2024:5773983}
    assert len(d)==21 and not d.ano.duplicated().any()
    assert d.set_index('ano').deficit_domicilios.to_dict()==expected
    assert d[['fonte_url','localizador_fonte','edicao_fonte','nota']].notna().all().all()
    assert d.loc[d.ano.eq(2010),'serie_metodologica'].item()=='Censo 2010'
    assert d.loc[d.ano.between(2016,2019),'edicao_fonte'].str.contains('reponderada').all()
    assert hashlib.sha256((ROOT/'data/processed/deficit_fjp_faixa_componente.csv').read_bytes()).hexdigest()=='63f3dd19837df0d40062eb39bc04106f41d8f9307f377cb86b1975a97c16308c'
    assert d.loc[d.ano.eq(2024),'deficit_domicilios'].item()==pd.read_csv(ROOT/'data/processed/deficit_fjp_total.csv').deficit_domicilios.item()
    fig=history_figure(d[d.ano>=2007])
    xs=[x for trace in fig.data for x in trace.x]
    assert 2020 not in xs and 2021 not in xs
    assert 2020 in fig.layout.xaxis.tickvals and 2021 in fig.layout.xaxis.tickvals
    assert all(trace.type=='bar' for trace in fig.data)
    # Regression for the user's screenshot, including the shared formatting layer.
    for start,end in [(2013,2024),(2007,2024),(2023,2024),(2024,2024)]:
        chart=history_figure(d[d.ano.between(start,end)])
        with patch('ui.st.plotly_chart'):
            plot(chart,'axis_regression')
        assert chart.layout.xaxis.type=='linear'
        assert list(chart.layout.xaxis.tickvals)==list(range(start,end+1))
        assert tuple(chart.layout.xaxis.range)==(start-.7,end+.7)
        for annotation in chart.layout.annotations:
            assert isinstance(annotation.x,int) and start<=annotation.x<=end
    for year in [1991,2010,2024]:
        single=history_figure(d[d.ano.eq(year)],ancient=year<2007)
        assert len(single.data)==1 and len(single.data[0].x)==1
    print('OK: 21 totais publicados, fontes, revisões, lacunas e gráficos; base 2022 intacta.')


if __name__=='__main__':
    main()
