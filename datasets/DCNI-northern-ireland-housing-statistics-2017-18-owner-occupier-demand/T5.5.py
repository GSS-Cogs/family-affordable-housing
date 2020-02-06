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
htype = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
Year = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
observations = htype.fill(DOWN).is_not_blank().is_not_whitespace() - tab.excel_ref('O11')
Dimensions = [
            HDim(Year,'Year', DIRECTLY,ABOVE),
            HDim(htype,'NI Housing Specification',DIRECTLY, LEFT),
            HDimConst('Unit','gbp'),  
            HDimConst('Measure Type','GBP Total'),
            HDimConst('NI Owner Occupied Housing Description','Northern Ireland Co-Ownership Housing Scheme Activity')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
table['Period'] = table['Year'].map(
    lambda x: f'gregorian-interval/{str(x)[:4]}-03-31T00:00:00/P1Y')
