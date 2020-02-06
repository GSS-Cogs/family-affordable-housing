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
cell = tab.filter(contains_string('Order Made'))
cell.assert_one()
Year = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
quarter = cell.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace() 
htype = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
observations = htype.fill(RIGHT).is_not_blank().is_not_whitespace() 
Dimensions = [
            HDim(Year,'Year',CLOSEST,LEFT),
            HDim(quarter,'quarter',DIRECTLY,ABOVE )
            HDimConst(htype,'NI Housing Specification',DIRECTLY,LEFT),
            HDimConst('Unit','applications'),  
            HDimConst('Measure Type','count'),
            HDimConst('NI Owner Occupied Housing Description','Orders Made in Relation to Mortgages')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
def user_perc(x):
    
    if ((str(x) ==  'Apr - Jun') :
        return 'Q1'
    elif ((str(x) ==  'Jul - Sep') :
        return 'Q2'
    elif ((str(x) ==  'Oct - Dec') :
        return 'Q3'
    elif ((str(x) ==  'Jan - Mar') :
        return 'Q4'
    else:
        return ''
new_table['quarter'] = new_table.apply(lambda row: user_perc(row['quarter']), axis = 1)
table['Period'] =  'year/' + table['Year'].astype(str).str[:4] + '-' + new_table['quarter']
table['Period'] = table['Period'].str.rstrip('-')
