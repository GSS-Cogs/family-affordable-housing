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
cell = tab.excel_ref('A3')
Year = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
grants = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = grants.fill(RIGHT).is_not_blank().is_not_whitespace()
measure = cell.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(Year,'Year',CLOSEST,LEFT),
            HDim(sap,'NI Household Energy',DIRECTLY,LEFT ),
            HDim(measure,'Unit',DIRECTLY,ABOVE),  
            HDimConst(measure,'Measure Type',DIRECTLY,ABOVE),
            HDimConst('NI Household Description','Northern Ireland Boiler Replacements Processed')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
table['Period'] = table['Year'].map(
    lambda x: f'gregorian-interval/{str(x)[:4]}-03-31T00:00:00/P1Y')
new_table['Geography'] = 'Northern Ireland'
