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
cell = tab.filter(contains_string('Region'))
cell.assert_one()
size = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
area = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = area.fill(DOWN).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(area, 'Geography',DIRECTLY,LEFT)
            HDim(size,'NI Household Characteristics',CLOSEST, LEFT),
            HDimConst('Unit','gbp'),  
            HDimConst('Measure Type','GBP Total'),
            HDimConst('NI Household Description','Northern Ireland weekly household income and expenditure')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'gregorian-interval/2015-03-31T00:00:00/P2Y'
