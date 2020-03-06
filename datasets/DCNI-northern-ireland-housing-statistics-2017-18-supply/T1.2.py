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
tab = tabs['T1.2']

# +
cell = tab.excel_ref('A3')
Year = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
area = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = Year.shift(0,2).fill(DOWN).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(Year,'Year',DIRECTLY,ABOVE),
            HDim(area,'Geography',DIRECTLY,LEFT),
            HDimConst('NI Housing Supply', 'Area Stock'),
            HDimConst('Unit','houses'),  
            HDimConst('Measure Type','Count'),
            HDimConst('NI Housing Description','Total Housing Stock in each Council Areas')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'year/' + new_table['Year']
new_table['Period'] = new_table['Period'].str.replace('\.0', '')
