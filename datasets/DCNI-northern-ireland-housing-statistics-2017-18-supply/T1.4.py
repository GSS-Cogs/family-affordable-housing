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
tab = tabs['T1.4']

# +
cell = tab.excel_ref('A3')
dwelling = cell.fill(RIGHT).is_not_blank().is_not_whitespace() 
area = cell.fill(DOWN).is_not_blank().is_not_whitespace()
observations = dwelling.fill(DOWN).is_not_blank().is_not_whitespace() - tab.excel_ref('F17')
Dimensions = [
            HDim(area,'Geography',DIRECTLY,LEFT),
            HDim(dwelling,'NI Housing Supply',DIRECTLY,ABOVE ),
            HDimConst('Unit','houses'),  
            HDimConst('Measure Type','Count'),
            HDimConst('NI Housing Description','Dwellings by Type in Councils')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'year/2018'
