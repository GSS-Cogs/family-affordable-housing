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
tab = tabs['T1.3']

# +
cell = tab.excel_ref('A3')
Year = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
supply = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = Year.shift(0,2).fill(DOWN).is_not_blank().is_not_whitespace() - tab.excel_ref('K14')
Dimensions = [
            HDim(Year,'Year',DIRECTLY,ABOVE),
            HDimConst('Geography','Northern Ireland'),
            HDim(supply,'NI Housing Supply',DIRECTLY,LEFT ),
            HDimConst('Unit','houses'),  
            HDimConst('Measure Type','Percentage'),
            HDimConst('NI Housing Description','Household Tenure')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'year/' + new_table['Year'].astype(str).str[:4]
new_table['Period'] = new_table['Period'].str.replace('\.0', '')
new_table['NI Housing Supply'] = new_table['NI Housing Supply'].str.rstrip('123457')
new_table['NI Housing Supply'] = new_table['NI Housing Supply'].map(
    lambda x: {
        'Bases=100%' : 'All Tenure'
        }.get(x, x))
def user_perc(x):
    
    if (str(x) ==  'All Tenure') : 
        
        return 'Count'
    else:
        return 'Percentage'
    
new_table['Measure Type'] = new_table.apply(lambda row: user_perc(row['NI Housing Supply']), axis = 1)
# -

new_table['NI Housing Supply'] = new_table['NI Housing Supply'].str.rstrip('4 ')
new_table['NI Housing Supply'] = new_table['NI Housing Supply'].str.lstrip(' ')
