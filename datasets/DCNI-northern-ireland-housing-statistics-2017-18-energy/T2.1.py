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
cell = tab.excel_ref('A4')
Year = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
heating = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = Year.shift(0,2).fill(DOWN).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(Year,'Year',DIRECTLY,ABOVE),
            HDim(neating,'NI Household Energy',DIRECTLY,LEFT ),
            HDimConst('Unit','houses'),  
            HDimConst('Measure Type','Count'),
            HDimConst('NI Household Description','Northern Ireland Household Central Heating By Fuel Type')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'year/' + new_table['Year']
new_table['Geography'] = 'Northern Ireland'
