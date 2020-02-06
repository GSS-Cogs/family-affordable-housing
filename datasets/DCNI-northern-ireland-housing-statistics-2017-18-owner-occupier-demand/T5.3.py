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
cell = tab.filter(contains_string('Property Type'))
cell.assert_one()
htype = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = tab.excel_ref('E3').fill(DOWN).is_not_blank().is_not_whitespace()
Dimensions = [
            HDimConst('Period', 'year/2018-Q3'),
            HDim(htype,'NI Housing Specification',DIRECTLY, LEFT),
            HDimConst('Unit','property'),  
            HDimConst('Measure Type','count'),
            HDimConst('NI Owner Occupied Housing Description','Northern Ireland Residential Property Standardised Price')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
