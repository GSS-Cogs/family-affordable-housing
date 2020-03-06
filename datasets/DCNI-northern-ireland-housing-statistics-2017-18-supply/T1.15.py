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

scraper = Scraper('https://www.communities-ni.gov.uk/publications/topic/8182?search=%22Northern+Ireland+Housing+Statistics%22&sort_by=field_published_date')
tabs = { tab.name: tab for tab in scraper.distributions[6].as_databaker() } 
tab = tabs['T1.15']

# +
cell = tab.excel_ref('A5')
area = tab.excel_ref('A').expand(DOWN).by_index([8,12,16,20,24,28,32,36,40,44,48,52,56])
supply = cell.fill(DOWN).is_not_blank().is_not_whitespace() - area
description = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
observations = description.shift(0,3).fill(DOWN).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(area,'Geography',CLOSEST,ABOVE),
            HDim(supply,'NI Housing Supply',DIRECTLY,LEFT ),
            HDimConst('Unit','applications'),  
            HDimConst('Measure Type','Count'),
            HDim(description,'NI Housing Description',DIRECTLY,ABOVE)
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'gregorian-interval/2017-03-31T00:00:00/P1Y'
# -
new_table['NI Housing Description'] = 'Residential Planning Decisions By Planning Authority' + new_table['NI Housing Description']

new_table['NI Housing Supply'] = new_table['NI Housing Supply'].map(
    lambda x: {
        '% Of Decisions Granted' : 'Percentage Of Decisions Granted'              
        }.get(x, x))


# +
def user_perc(x):
    
    if (str(x) ==  'Percentage Of Decisions Granted') : 
        
        return 'Percentages'
    else:
        return 'Count'
    
new_table['Measure Type'] = new_table.apply(lambda row: user_perc(row['NI Housing Supply']), axis = 1)
