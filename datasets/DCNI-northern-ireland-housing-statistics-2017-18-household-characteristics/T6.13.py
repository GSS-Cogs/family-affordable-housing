# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from gssutils import *

# +
cell = tab.filter(contains_string('New Local Government District'))
cell.assert_one()
area = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = tenure.fill(RIGHT).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(area,'Geography',DIRECTLY,LEFT),
            HDimConst('NI Household Characteristics','Average Rates Bill'),
            HDimConst('Unit','gbp'),  
            HDimConst('Measure Type','GBP Total'),
            HDimConst('NI Household Description','Northern Ireland Households Average Rates Bill By New Local Government District')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
table['Period'] = 'gregorian-interval/2017-03-31T00:00:00/P1Y')
