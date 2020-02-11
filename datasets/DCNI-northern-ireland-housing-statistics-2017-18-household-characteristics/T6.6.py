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
cell = tab.filter(contains_string('Household Type'))
cell.assert_one()
size = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
ttype = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = size.shift(0,3).fill(DOWN).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(ttype, 'ttype',DIRECTLY,LEFT)
            HDim(size,'NI Household Characteristics',DIRECTLY,ABOVE),
            HDimConst('Unit','number'),  
            HDimConst('Measure Type','Count'),
            HDimConst('NI Household Description','Northern Ireland Dwelling Type')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'year/2016'
new_table['NI Household Characteristics'] = new_table['NI Household Characteristics'] + '' + new_table['ttype']
new_table['NI Household Characteristics'] = new_table['NI Household Characteristics'].map(
    lambda x: {
        'Owner' : 'Owner Occupied'
        }.get(x, x))
new_table['Geography'] = 'Northern Ireland'
