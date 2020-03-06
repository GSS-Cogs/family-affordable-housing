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
tab = tabs['T1.5']

# +
cell = tab.excel_ref('A3')
dwelling = cell.fill(DOWN).is_not_blank().is_not_whitespace() 
year = cell.fill(RIGHT).is_not_blank().is_not_whitespace()
measure = cell.shift(0,2).fill(RIGHT).is_not_blank().is_not_whitespace()
observations = measure.fill(DOWN).is_not_blank().is_not_whitespace() - tab.excel_ref('R11')
Dimensions = [
            HDimConst('Geography','Northern Ireland'),
            HDim(dwelling,'NI Housing Supply',DIRECTLY,LEFT),
            HDim(year,'Year',CLOSEST,LEFT),
            HDimConst('Unit','houses'),  
            HDim(measure,'Measure Type', DIRECTLY,ABOVE),
            HDimConst('NI Housing Description','Unfitness and Basic Amenities')
    
]  
c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
new_table = c1.topandas()
import numpy as np
new_table.rename(columns={'OBS': 'Value','DATAMARKER': 'NI Marker'}, inplace=True)
new_table['Period'] = 'year/' + new_table['Year']
new_table['Measure Type'] = new_table['Measure Type'].map(
    lambda x: {
        'Number' : 'Count', 
        '%' : 'Percentage'
        }.get(x, x))
new_table['NI Housing Supply'] = new_table['NI Housing Supply'].map(
    lambda x: {'Dwellings Lacking One Or ' : 'Dwellings Lacking One Or More Basic Amenities'
        }.get(x, x))
