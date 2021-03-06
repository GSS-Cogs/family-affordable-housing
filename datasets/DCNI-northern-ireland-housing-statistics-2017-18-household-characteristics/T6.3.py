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
cell = tab.filter(contains_string('Area'))
cell.assert_one()
Year = cell.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace() 
size = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
area = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = Year.shift(0,1).fill(DOWN).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(Year,'Year',DIRECTLY,ABOVE),
            HDim(area, 'Geography',DIRECTLY,LEFT)
            HDim(size,'NI Household Characteristics',CLOSEST, LEFT),
            HDimConst('Unit','people'),  
            HDimConst('Measure Type','Count'),
            HDimConst('NI Household Description','Northern Ireland Household by Local Government District')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = new_table['Year'].map(
    lambda x: {
        '2012' : 'year/2012', 
        '2022' : 'year/2022',
        '2037': 'year/2037' ,
        '2012-2037': 'gregorian-interval/2012-03-31T00:00:00/P15Y',
        '2012-2022': 'gregorian-interval/2012-03-31T00:00:00/P10Y'
        }.get(x, x))
