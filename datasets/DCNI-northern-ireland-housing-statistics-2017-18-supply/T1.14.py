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
tab = tabs['T1.14']

# +
cell = tab.excel_ref('A3')
supply = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
area = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
observations = supply.fill(DOWN).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(area,'Geography',DIRECTLY,LEFT),
            HDim(supply,'NI Housing Supply',DIRECTLY,ABOVE ),
            HDimConst('Unit','applications'),  
            HDimConst('Measure Type','Count'),
            HDimConst('NI Housing Description','Residential Planning Applications and Decisions By Planning Authority')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'gregorian-interval/2017-03-31T00:00:00/P1Y'
# -
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
