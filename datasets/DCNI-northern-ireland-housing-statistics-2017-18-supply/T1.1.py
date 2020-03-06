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
tab = tabs['T1.1']

# +
cell = tab.excel_ref('A3')
Year = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
area = tab.excel_ref('A').expand(DOWN).by_index([6,16,26])
supply = cell.fill(DOWN).is_not_blank().is_not_whitespace() - area
observations = Year.shift(0,2).fill(DOWN).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(Year,'Year',DIRECTLY,ABOVE),
            HDim(area,'Geography',CLOSEST,ABOVE),
            HDim(supply,'NI Housing Supply',DIRECTLY,LEFT ),
            HDimConst('Unit','houses'),  
            HDimConst('Measure Type','Count'),
            HDimConst('NI Housing Description','Key Housing Supply')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['NI Housing Supply'] = new_table['NI Housing Supply'].str.rstrip('123457')
def user_perc(x):
    
    if ((str(x) ==  '2008-09') | (str(x) == '2009-10')) | ((str(x) == '2010-11')): 
        
        return 'year/' + str(x)[0:4]
    else:
        return 'gregorian-interval/' + str(x)[0:4] + '-03-31T00:00:00/P1Y'
    
new_table['Period'] = new_table.apply(lambda row: user_perc(row['Year']), axis = 1)
# -


