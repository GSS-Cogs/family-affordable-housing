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
cell = tab.filter(contains_string('Year'))
cell.assert_one()
Year = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
quarter = cell.shift(1,0).fill(DOWN).is_not_blank().is_not_whitespace()
htype = cell.shift(2,0).fill(RIGHT).is_not_blank().is_not_whitespace()
observations = htype.fill(DOWN).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(Year,'Year', CLOSEST,ABOVE),
            HDim(quarter,'quarter',DIRECTLY,LEFT ),
            HDim(htype,'NI Housing Specification',DIRECTLY, ABOVE),
            HDimConst('Unit','property'),  
            HDimConst('Measure Type','count'),
            HDimConst('NI Owner Occupied Housing Description','Number of Verified Property Sales in Northern Ireland')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['quarter'] = new_table['quarter'].map(
    lambda x: {
        'Quarter 1' : 'Q1', 
        'Quarter 2' : 'Q2', 
        'Quarter 3' : 'Q3', 
        'Quarter 4' : 'Q4'       
        }.get(x, x))
new_table['Period'] = 'quarter/' + new_table['Year'].astype(str) + '-' + new_table['quarter'].astype(str)
