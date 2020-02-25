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
cell = tab.filter(contains_string('Tenure'))
cell.assert_one()
tenure = cell.fill(DOWN).is_not_blank().is_not_whitespace()
income = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
observations = tenure.fill(RIGHT).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(tenure,'NI Household Characteristics',DIRECTLY, LEFT),
            HDimConst('Unit','gbp'),  
            HDimConst('Measure Type','GBP Total'),
            HDim(income, 'NI Household Description',DIRECTLY,ABOVE)
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'gregorian-interval/2015-03-31T00:00:00/P2Y'
new_table['NI Household Characteristics'] = 'Tenure ' + new_table['NI Household Characteristics']
new_table['NI Household Description'] =  'Northern Ireland household Source of Income' + new_table['NI Household Description']
new_table['Geography'] = 'Northern Ireland'
