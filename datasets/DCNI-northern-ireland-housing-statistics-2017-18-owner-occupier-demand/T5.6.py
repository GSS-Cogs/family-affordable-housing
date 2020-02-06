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
htype = cell.fill(RIGHT).is_not_blank().is_not_whitespace() \
            .filter(lambda x: type(x.value) != 'Percentage' not in x.value) \
            .filter(lambda x: type(x.value) != '%' not in x.value)
observations = htype.fill(DOWN).is_not_blank().is_not_whitespace() - tab.excel_ref('K25')
Dimensions = [
            HDim(Year,'Year', DIRECTLY,LEFT),
            HDim(htype,'NI Housing Specification',DIRECTLY,ABOVE),
            HDimConst('Unit','gbp'),  
            HDimConst('Measure Type','GBP Total'),
            HDimConst('NI Owner Occupied Housing Description','Northern Ireland First-time Buyers Lending and Affordability')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
table['Period'] =  'year/' + table['Year'].astype(str)
